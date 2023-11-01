# Yelp Web Crawler

## Overview
The Yelp Web Crawler is a python script developed using Scrapy library to scrape data from Yelp
business listings.

## Project Description
* The main scrapping logic you can check in `crawling_spiders.py`
* The included JSON file is an example, of the data to be scrapped and how it would be structured. 
In this case, `location = San Francisco, CA`, `category = Contractors`. 

***
## Installation
1. Clone this repository to your local machine.
```shell
git clone https://github.com/dmytriibasov/yelp_crawler.git
```
2. Navigate to the project directory:  
```shell 
cd yelp_crawling
```
3. Install required packages:  
```shell 
pip install -r requirements.txt
```
***
## Usage
To use this crawler, follow next steps:
1. Run the crawler passing the necessary args, like `location` and `category`:  
```shell
scrapy crawl yelp_crawl yelp_crawler -a location="Your Location" -a category="Your Category"
```
2. The crawler will scrape data from Yelp business listings and stream it into a JSON file.
