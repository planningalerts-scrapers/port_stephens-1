# Parsing HTML
from bs4 import BeautifulSoup
# Submitting forms
import mechanize
# To format date in the required format
import datetime
# To parse a string into a date
import dateutil.parser
# To convert relative URLs into absolute URLs
from urlparse import urljoin
# To write to CSV for testing
import csv
# To write to SQLite database
import scraperwiki

# Consts
url = "http://datracker.portstephens.nsw.gov.au/Application/AdvancedSearchResult?DateFrom=15/06/2015&DateTo=17/06/2015&DateType=1&ApplicationType=16,9,25&ShowOutstandingApplications=False&ShowExhibitedApplications=False&IncludeDocuments=False"

# Use mechanize to fetch the webpage, ignoring robots.txt so we don't get 403.
br = mechanize.Browser()
br.set_handle_robots(False)
response1 = br.open(url)

# Submit the "I agree" form
br.select_form(nr=0)
br.form.set_all_readonly(False)

#<input type="submit" name="ctl00$ctMain$BtnAgree" value="I Agree" id="ctl00_ctMain_BtnAgree" style="padding:8px; border: 1px solid gray;">
#<button id="agree" type="button" class="btn btn-primary">Agree</button>
#<input id="agreed" name="agreed" type="hidden" value="False">
#response2 = br.submit(name="agreed")
br.form.controls[0].value = 'True'
response2 = br.submit()

d = response2.read()
bsd = BeautifulSoup(d)

import pdb;pdb.set_trace()
# Get results list
result = bsd.find_all(id="hiddenresult")[0]
children = result.findChildren("div",{'class': 'result'})

for child in children:

    da = {}
    
    # Required fields

    """
    The ID that the council has given the planning application. 
    This also must be the unique key for this data set.
    """
    council_reference = ""

    a = child.findChildren("a", {"class":"search"})[0]
    council_reference = a.text.encode("utf8")
    
    da["council_reference"] = council_reference

    """
    The physical address that this application relates to. This will be 
    geocoded so doesn't need to be a specific format but obviously the more 
    explicit it is the more likely it will be successfully geo-coded. If the 
    original address did not include the state (e.g. "QLD") at the end, then 
    add it.
    """
    address = ""
    
    strong = child.findChildren("strong")[0]
    address = strong.text.encode("utf8")
    
    # Tidy up the address format
    address = address.replace("\r", ", ")
    address = address.replace("/ ", "/")
    address = " ".join(address.split()) 
    
    da["address"] = address

    """
    A text description of what the planning application seeks to carry out.
    """
    description = ""
    
    description_element = child.find_all('br')[0].next_sibling
    last_part_of_string = description_element.split('-')[-1]
    description = last_part_of_string.encode("utf8").strip()
    
    da["description"] = description

    """
    URL that provides more information about the planning application.
    This should be a persistent URL that preferably is specific to this 
    particular application. In many cases councils force users to click 
    through a license to access planning application. In this case be 
    careful about what URL you provide. Test clicking the link in a browser 
    that hasn't established a session with the council's site to ensure users 
    of PlanningAlerts will be able to click the link and not be presented with 
    an error.
    """
    info_url = ""
    
    a = child.findChildren("a", {"class":"search"})[0]
    relative_link = a.get('href')
    info_url = urljoin(url, relative_link)
    
    da["info_url"] = info_url

    """
    A URL where users can provide a response to council about this particular 
    application.
    As in info_url this needs to be a persistent URL and should be specific 
    to this particular application if possible. Email mailto links are also 
    valid in this field.
    """
    comment_url = ""
    
    comment_url = info_url
    
    da["comment_url"] = comment_url

    """
    The date that your scraper is collecting this data (i.e. now). Should 
    be in ISO 8601 format.
    Use the following Ruby code: Date.today.to_s
    """
    date_scraped = datetime.date.today().isoformat()
    da["date_scraped"] = date_scraped
    
    # Optional fields
    
    """
    The date this application was received by council. Should be in ISO 8601 
    format.
    """
    date_received = ""
    
    lodged_string = child.find('div').contents[0]
    date_string = lodged_string.split(':')[1].strip().encode("utf8")
    
    lodged_date = dateutil.parser.parse(date_string, 
        default=datetime.date.today(), dayfirst=True)
    date_received = lodged_date.isoformat()
    
    da["date_received"] = date_received
    
    """
    The date from when public submissions can be made about this application. 
    Should be in ISO 8601 format.
    """
    on_notice_from = ""
    
    """
    The date until when public submissions can be made about this application. 
    Should be in ISO 8601 format.
    """
    on_notice_to = ""
    
    scraperwiki.sqlite.save(unique_keys=['council_reference'], data=da)
