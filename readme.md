# Vaccine Appointment Scanner
This script checks the macovidvaccines site for sites that have slots open for vaccination appointments. For each clickable signup option, it will also open that page in another browser tab, to get you started on the signup process yourself. The script will also send you a text message using Twilio if there are sites with open appointments.

# Requirements and limitations
* Selenium Webdriver and Chrome
* Script uses configparser and argparser
* It is written only for Chrome browser
* It is written to use only sms from Twilio
* Some sites have specific restrictions, for example you must live in a certain community, or you must have a certain career like healthcare worker or educator. This script clicks the signup button for those sites anyway. Make sure you read the restrictions before continuing the signup process, or else you may end up being denied a shot when you show up at the scheduled time!


# Usage tips
python scan_for_appointment.py --zip _zipcode_ --distance _search_dist_

Keep in mind the state guidelines for eligibility. Don't jump the line. This script won't lie for you, but it will make it easier for you to lie. Don't. I wrote this script only because once it _is_ your turn in line, you'll be hard pressed to find an open slot.

I suggest you use python virtual environments to install selenium and twilio libraries and keep this env separate from your default environment. I have used pipenv (Pipfile) but also provided a requirements.txt (this part is untested).

Appointments for vaccinations fill up very quickly - often in less than five minutes. I highly recommend you have cached pharmacy credentials in Chrome: create accounts at CVS, Walgreens, and other sites, to make it easier for you to continue the signup process after this script runs.

The chromedriver only gets closed if there are no slots available. If there are, you'll need to dismiss the window manually before running the script again, otherwise you'll get an invalid argument exception about the data profile path being in use.

## ini file
The Chromedriver in Selenium will use your profile but you will need to change the default in my-settings.ini. You don't have to use your own profile, but if you don't, there will be no cached credentials so you will be a little slower to grab that appointment slot. Find your **userprofile** by navigating to _chrome://version_ in the address bar and find your Profile Path. **chromedriver** is where you installed the selenium Chromedriver binary.

The notify section should contain your telephone number so that you can send yourself an **sms** text message. I have only tested my US-based telephone number (+1<ten_digits>). Don't include this section (or keep the sms value blank) if you don't want text message notification.

## environment
This script presumes you have set up some environment variables for a Twilio account. The SID and TOKEN represent your account and the token to access the Twilio REST API. The PHONE is the free phone number you can get from Twilio.

# Possible next steps
* Set this up to run periodically. However, this will also send text messages periodically, so watch out for data message rates.
* Expand to a variety of selectable notification methods (twitter, email, etc), and don't rely on Twilio.
* Do a way better job of handling the Xpath elements. This was quickly cobbled together, is inefficient and ugly.
* Handle the distance setting better; radio buttons changed from 5, 10, 25 at one point to 10, 25, 50 and I had to change code for that. Should be able to dynamically build this list.
* Allow a way to identify which site(s) should be ignored the next time the script is run. If your search distance pulls up sites close enough to you but that have residency requirements you don't meet, for example, it would be nice to ignore that site the next time the script is run.
* Support other browsers.
