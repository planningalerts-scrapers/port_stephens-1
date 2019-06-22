require "masterview_scraper"

MasterviewScraper.scrape_and_save_period(
  url: "http://datracker.portstephens.nsw.gov.au",
  period: :thismonth,
  use_api: true,
  long_council_reference: true,
  types: [16, 9, 25]
)
