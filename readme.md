# ScraPi

General webscraping tool I created that allows one to periodically scrape sources and check for updates.


Ideas to implement:
* refactor into flask server, have GUI to read the JSONs
* have a button to enable/disable sources
* add command line args for individual scrapers
* batch exceptions together for email notification; for example, add feature where a scraper is only taken offline after it gets 3 exceptions in current session or within X hours. Only then would you disable it and send an email.
