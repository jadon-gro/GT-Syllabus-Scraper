# GT-Syllabus-Scraper
Scraper intended to grab and parse PDFs of GT Syllabi from the internet.
The work for this project was done almost entirely in early Spring 2021 so details on this are a little hazy for me.

## Files

scraper.py in the main directory is the main scraping code.

I've included folders for departments PDFs we've been able to scrape as example output.

The topic_list.json files are examples of the topic list parsing functionality. The scraper is also able to isolate topic lists for classes and convert them to Strings using an OCR.


## Functionality
Right now this only works for most engineering schools. Each department and school has their own way of uploading course syllabi (or none at all) so a universal scraper is more than difficult. Most engineering departments have PDF versions of their syllabi which make downloading easy, but ECE does not. For ECE, we convert the relevant section of the HTML into a PDF.

This code is also capable of isolating course topic lists as strings using an OCR. This allows us to display course topics in our website in the catalog. This requires us to be able to parse the syllabi looking for key words that usually wrap the topic list. This is still a little hit or miss with some departments such as NRE but usually works.

## Notes and Acknowledgements
This was created for a student-led course registration platform called BuzzBook. Georgia Tech updated their system and made most of our features obsolete so the club was disbanded. This code was written primarily by myself but with help from the platform's leader Ed Chen. Thanks so much!
