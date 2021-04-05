from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import argparse
import configparser
from twilio.rest import Client
import os

# for notification, use your own free twilio account
TWILIO_SID = os.environ['TWILIO_SID']
TWILIO_TOKEN = os.environ['TWILIO_TOKEN']
TWILIO_PHONE = os.environ['TWILIO_PHONE']

# distances as used by macovidvaccines
allowed_dist = [10, 25, 50] # round any distance lower than each to the next one up
any_dist = 9999 # this is considered 'any'


""" gather list of hits from macovidvaccines site
  zip = string representing zip code
  distance = int representing distance value (-1 (=any), 10, 25, 50)
"""
def gather_sites(driver, zip, distance):
    # if distance not valid, make it 'any'
    if distance not in allowed_dist:
        distance = any_dist # this is considered 'any'
    radio_elem_xp = "//input[@type='radio'][@value='{}']".format(str(distance))
    available_check = driver.find_element_by_name('onlyShowAvailable')
    if not available_check.is_selected():
        available_check.click()
    # clear previous, otherwise we may have two zipcodes in there
    driver.find_element_by_name('zip-code').send_keys(Keys.CONTROL + "a")
    driver.find_element_by_name('zip-code').send_keys(zip)

    dist_opt = driver.find_element_by_xpath(radio_elem_xp)
    dist_opt.click()

    apply_filt = driver.find_element_by_xpath("//button[contains(.,'Apply Filters')]")
    apply_filt.click()

""" send notification to user there are slots available
  notify_config = config object from ConfigParser
  message = string message
"""
def send_notify(notify_config, message):
    # verify notify specification and that sms isn't empty(ish)
    if notify_config != None and 'sms' in notify_config and len(notify_config['sms'])>4:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        message = client.messages.create(
            to=notify_config['sms'],
            from_=TWILIO_PHONE,
            body=message
        )
    else:
        print("No valid notification spec")


# Arguments for zip and distance
parser = argparse.ArgumentParser(description="Find available covid vaccine appointments in Massachusetts and open Chrome tabs to sign up for each")
parser.add_argument('--zip', default='02134', type=ascii, help='five-digit zip code to search for')
parser.add_argument('--distance', default=10, type=int, help='search distance (10, 25, 50, or -1 for any distance)')
args=parser.parse_args()
# args.zip
# args.distance
if args.distance == -1:
    args.distance = any_dist # special case
else:
    # round up to next valid distance
    for i in allowed_dist:
        if args.distance <= i:
            args.distance = i
            break

# Config file for Chrome user information and SMS information
config = configparser.ConfigParser()
config.read('my-settings.ini')
chromespec = None if 'CHROMESPEC' not in config else config['CHROMESPEC']
notifyspec = None if 'NOTIFY' not in config else config['NOTIFY']

if chromespec == None:
    driver = webdriver.Chrome()
else:
    options = webdriver.ChromeOptions()
    options.add_argument("user-data-dir={}".format(chromespec['userprofile']))
    driver = webdriver.Chrome(executable_path=chromespec['chromedriver'], options=options)
driver.get('https://www.macovidvaccines.com/')
gather_sites(driver, args.zip, args.distance)

# mm/yy/dd: n slots
pattern = re.compile(r".*\d{1,2}\/\d{1,2}\/\d{2}: (\d{1,4}) slot.*")
#clickable_signup = "MuiButtonBase-root MuiButton-root MuiButton-contained MuiButton-containedSecondary"
#wrap_list = driver.find_element_by_xpath('//div[@id="progress"]/div[@class="loadedContent"]/div[@role="list"]')
items = driver.find_elements_by_xpath('//div[@role="listitem"]')
known_list = []   # sites that display known number of slots
known_names = []
unknown_list = [] # sites (like CVS) that do not display number of slots
known_count = 0   # sum of all slots over all known sites
unk_count = 0     # sum of all "unknown" sites
for item in items:
    for aline in item.text.splitlines():
        match = pattern.match(aline)
        if match:
            known_count += int(match.group(1))
            known_list.append(item)
            # the name of the location is identified by MuiCardHeader-title span class
            known_names.append(item.find_element_by_xpath('.//span[contains(@class, "MuiCardHeader-title")]').text)
        elif re.compile(r".*isn't providing details.*").match(aline):
            unk_count += 1
            unknown_list.append(item)

print("--------------------------------------")
print("Found {} slots-locations".format(str(known_count)), end=": ")
print(*known_names, sep=", ")
print("Found {} locations with TBD slot count".format(str(len(unknown_list))))
if len(known_list)+len(unknown_list):
    for site in known_list + unknown_list:
        try:
            # signup button distinguished by class MuiButton-root
            site.find_element_by_xpath('.//a[contains(@class, "MuiButton-root")]').click()
        except:
            print("fail to find sign-up button for {}".format(site.text))
    print("Subtabs have been opened")
    send_notify(notifyspec,
        "Found {} slots-locations and {} TBD slots. Check chromedriver.".format(str(known_count), str(len(unknown_list))))
else:
    driver.close()
print("--------------------------------------")
