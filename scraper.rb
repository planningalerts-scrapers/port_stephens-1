require "masterview_scraper"

MasterviewScraper.scrape_and_save_period(
  url: "http://datracker.portstephens.nsw.gov.au",
  period: :last30days,
  use_api: true
)
