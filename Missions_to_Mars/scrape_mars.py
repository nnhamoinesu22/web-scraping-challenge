import pandas as  pd
from sqlalchemy import create_engine
from splinter import Browser
from bs4 import BeautifulSoup
import requests
import shutil
import time

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

def scrape_info():
    browser = init_browser()

    news_title = scrape_mars_news()
    news_p = scrape_mars_news()
    featured_image_url = scrape_mars_featured_image()
    mars_weather = scrape_mars_weather()
    tweet_img_link = scrape_mars_weather()
    mars_df_table_data_html = scrape_mars_facts()
    mars_hemispheres = scrape_mars_hemispheres()

    mars_info_dict = {}
    mars_info_dict["news_title"] = news_title
    mars_info_dict["news_p"] = news_p
    mars_info_dict["featured_image_url"] = featured_image_url 
    mars_info_dict["mars_weather"] = mars_weather
    mars_info_dict["tweet_img_link"]= tweet_img_link
    mars_info_dict["mars_facts"] = mars_df_table_data_html
    mars_info_dict["mars_hemispheres"] = mars_hemispheres

    browser.quit()
    return mars_info_dict
    
def scrape_mars_news():
    browser = init_browser()

    news_url = "https://mars.nasa.gov/news/"
    browser.visit(news_url)
    time.sleep(3)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    latest_news_article = soup.find("div", class_='list_text')
    news_title = latest_news_article.find("div", class_="content_title").text
    news_p = latest_news_article.find("div", class_ ="article_teaser_body").text

    browser.quit()
    return news_title,news_p

def scrape_mars_featured_image():
    browser = init_browser()
    image_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(image_url)
    time.sleep(3)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    image = soup.find("img", class_="thumb")["src"]
    featured_image_url = "https://www.jpl.nasa.gov" + image
     

    browser.quit()
    return featured_image_url
    
def scrape_mars_weather():
    browser = init_browser()
    tweet_url = "https://twitter.com/marswxreport?lang=en"
    tweet_html_content = requests.get(tweet_url).text
    soup = BeautifulSoup(tweet_html_content, "lxml")
    latest_tweet = soup.find_all('div', class_="js-tweet-text-container")


    #empty list to hold tweet we are going to keep, used to strip useless content from string
    tweets_list = []
    # Loop that scans every tweet and searches specifically for those that have weather info
    for tweets in latest_tweet: 
        tweet_body = tweets.find('p').text
        if 'InSight' and 'sol' in tweet_body:
            tweets_list.append(tweet_body)
            #break statement to only print the first weather tweet found
            break
        else: 
            #if not weather related skip it and try again
            pass
        
    #cleaned up tweet removes unncessary link to twitter image included in string, :-26 removes the last 26 characters which is the length of the img url
    #after reviewing several links they all appear to work with the value of -26
    mars_weather = ([tweets_list[0]][0][:-26])
    tweet_img_link = ([tweets_list[0]][0][-26:])
    return mars_weather,tweet_img_link
    
def scrape_mars_facts():
    browser = init_browser()
    mars_facts_url = "https://space-facts.com/mars/"
    browser.visit(mars_facts_url)


    mars_facts_read_html = pd.read_html(mars_facts_url)
    mars_facts_df = pd.DataFrame(mars_facts_read_html[0])
    mars_facts_df.columns = ['Mars','Data']
    mars_df_table= mars_facts_df.set_index("Mars")
    mars_df_table_data = mars_df_table.to_html(classes='marsdata')
    mars_df_table_data_html = mars_df_table_data.replace('\n', ' ')
    

    browser.quit()
    return mars_df_table_data_html
    
def scrape_mars_hemispheres():
#MARS Hemispheres
    mars_hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(mars_hemispheres_url)

    hemisphere_image_urls = []
    for i in range(4):

        # Find the elements on each loop to avoid a stale element exception
        browser.find_by_css("a.product-item h3")[i].click()

        hemi_data = scrape_hemisphere(browser.html)

        # Append hemisphere object to list
        hemisphere_image_urls.append(hemi_data)

        # Finally, we navigate backward
        browser.back()

    return hemisphere_image_urls

def scrape_hemisphere(html_text):

    # Soupify the html text
    hemi_soup = BeautifulSoup(html_text, "html.parser")

    # Try to get href and text except if error.
    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text="Sample").get("href")

    except AttributeError:

        # Image error returns None for better front-end handling
        title_elem = None
        sample_elem = None

    mars_hemispheres = {
        "title": title_elem,
        "img_url": sample_elem
    }

    return mars_hemispheres
    

#if __name__ == "__main__":
 #   print(scrape_info())
    #return mars_info_dict
