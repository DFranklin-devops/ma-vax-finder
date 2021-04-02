from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re


""" gather list of hits from macovidvaccines site
  zip = string representing zip code
  distance = string representing distance value ("any", "5", "10", "25")
"""
def gather_sites(driver, zip, distance):
    if distance not in ["5", "10", "25"]:
        distance = "9999" # this is considered 'any'
    radio_elem_xp = "//input[@type='radio'][@value='{}']".format(distance)
    available_check = driver.find_element_by_name('onlyShowAvailable')
    if not available_check.is_selected():
        available_check.click()
    zip_code = driver.find_element_by_name('zip-code')
    dist_25 = driver.find_element_by_xpath(radio_elem_xp)
    zip_code.send_keys(zip)
    dist_25.click()
    apply_filt = driver.find_element_by_xpath("//button[contains(.,'Apply Filters')]")
    apply_filt.click()

driver = webdriver.Chrome()
driver.get('https://www.macovidvaccines.com/')
gather_sites(driver, "01748","35")

pattern = re.compile(r".*\d{1,2}\/\d{1,2}\/\d{2}: (\d{1,4}) slot.*")
clickable_signup = "MuiButtonBase-root MuiButton-root MuiButton-contained MuiButton-containedSecondary"

#wrap_list = driver.find_element_by_xpath('//div[@id="progress"]/div[@class="loadedContent"]/div[@role="list"]')
#print(len(wrap_list))
items = driver.find_elements_by_xpath('//div[@role="listitem"]')
known_count = 0
unk_count = 0
known_list = []
unknown_list = []
for item in items:
    for aline in item.text.splitlines():
        match = pattern.match(aline)
        if match:
            known_count += int(match.group(1))
            known_list.append(item)
#            try:
#                item.find_element_by_xpath('.//a[@class="{}"]'.format(clickable_signup)).click()
#            except:
#                print("fail to find sign-up button for {}".format(item.text))
        elif re.compile(r".*isn't providing details.*").match(aline):
            unk_count += 1
            unknown_list.append(item)
#            try:
#                item.find_element_by_xpath('.//a[@class="{}"]'.format(clickable_signup)).click()
#            except:
#                print("fail to find sign-up button for {}".format(item.text))
        # click sign up button


print("--------------------------------------")
print("Found {} slots in {} locations".format(str(len(known_list)), str(len(known_list)-len(unknown_list))))
print("Found {} locations with TBD slot count".format(str(len(unknown_list))))
if len(known_list)+len(unknown_list):
    for site in known_list + unknown_list: #.extend(unknown_list):
        try:
            site.find_element_by_xpath('.//a[@class="{}"]'.format(clickable_signup)).click()
        except:
            print("fail to find sign-up button for {}".format(site.text))
    print("Subtabs have been opened")
print("--------------------------------------")
#    element_text = item.text
#    element_attribute_value = item.get_attribute('total-available')

#    print(item)
#    print('element.text: {0}'.format(element_text))
#    print("----------------------------------------------------------------")
#    print('element.get_attribute(\'value\'): {0}'.format(element_attribute_value))

#driver.close()
