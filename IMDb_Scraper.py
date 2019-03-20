#!/usr/bin/env python
# coding: utf-8

# Movie Scripts

# In[1]:


from requests import get
from bs4 import BeautifulSoup
import re
import pandas as pd
from time import sleep
from random import randint
from time import time
from IPython.core.display import clear_output
from warnings import warn
from pytube import YouTube
import pytube
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import math
import cv2
import os
import unicodedata
import string


# In[2]:


valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
char_limit = 255

def clean_filename(filename, whitelist=valid_filename_chars, replace=' '):
    # replace spaces
    for r in replace:
        filename = filename.replace(r,'_')
    
    # keep only valid ascii chars
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()
    
    # keep only whitelisted chars
    cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
    if len(cleaned_filename)>char_limit:
        print("Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(char_limit))
    return cleaned_filename[:char_limit]    


# In[ ]:


# Store data in lists
names = []
runtimes = []
profile_pages = []
# storylines = []
release_dates = []
budgets = []
plot_synopsis = []
production_companies = []
spec_eff_comps = []
gross = []
stars = []
directors = []
screen_writers = []
metascores = []
genres = []
mpaa_ratings = []
imdb_ratings = []
movie_awards = []
movie_reviews = []
key_frame_exception = []

# pages = [str(i) for i in range(1,141000,250)]
pages = ['1']

#Prepare monitoring of loop
start_time = time()
requests = 0
#for every page
for page in pages:

    #make get request
    response = get("https://www.imdb.com/search/title?title_type=feature&languages=en&count=50&start=" + page)

    #pause the loop
    sleep(randint(8,15))

    #monitor requests
    requests += 1
    elapsed_time = time() - start_time
    print('Request:{}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
    clear_output(wait = True)

    #throw a warning for non-200 status codes
    if response.status_code != 200:
        warn('Request: {}; Status code: {}'.format(requests, response.status_code))

    #break the loop if the number of requests is greater than expected
    if requests > 72:
        warn('Number of requests was greater than expected.')
        break

    # parse the content of request
    page_html = BeautifulSoup(response.text, 'html.parser')

    #select all 250 movie containers from a single page
    mv_containers = page_html.find_all('div', class_ = 'lister-item mode-advanced')

    # Extract data from indiv. movie containers
    for container in mv_containers:
        if container.find('div', class_ = 'ratings-metascore') is not None:
            #Name
            name = container.h3.a.text
            names.append(name)
            
            #Runtime
            runtime = container.find('span', class_ = 'runtime').text
            runtimes.append(runtime)
                        
            #Stars
            movie_stars = []
            stars_x = container.findAll('div')[3].findAll('p')[2].findAll('a')
            del stars_x[0]
            for star in stars_x:
                movie_stars.append(star.text)
            stars.append(movie_stars)

            #Profile
            sleep(randint(1,3))
            profile = container.h3.a['href']
            profile_pages.append(profile)

            details = get("https://www.imdb.com/" + profile)
            # parse the content of request
            details_html = BeautifulSoup(details.text, 'html.parser')

            #save storyline
#             storyline = details_html.find("div", {"id": "titleStoryLine"}).div.span.text
#             storylines.append(storyline)
            
            try:
                #Budget
                bo_budget = details_html.find(text='Budget:').parent.findNext('span').decompose()
                budget = details_html.find(text='Budget:').parent.parent.text.strip()
                budgets.append(budget[7:].replace('$', '').replace(',', ''))
            except:
                budgets.append("null")
                    
            #Release Dates
            html_text = "Release Date:"
            details_html.find(text='Release Date:').parent.findNext('span').decompose()
            date = details_html.find(text='Release Date:').parent.parent.text.strip()
            release_dates.append(re.sub(r'\([^)]*\)', '', date[14:])[:-1])
            
#             movie_name = name
#             award = get("https://www.boxofficemojo.com/oscar/movies/?id={}.htm".format(movie_name.replace(" ", "")))
#             html_awards = BeautifulSoup(award.text, 'html.parser')
#             award_links = html_awards.find("div", {"id": "body"}).find_all('a')
#             awards = {}
#             for award in award_links:
#                 if "(WIN)" in award.text:
#                     link = "https://www.boxofficemojo.com/{}".format(award['href'])
#                     new_url = link
#                     new_response = get(link)
#                     html_award = BeautifulSoup(new_response.text, 'html.parser')
#                     html_award.find('font').extract()
#                     title = html_award.find('font').text
#                     if title == "BEST PICTURE":
#                         awards[title] = movie_name
#                     else:
#                         awards[title] = html_award.find(text=movie_name).findNext('font').text
            
            #Production Companies
            production_comps = []
            sleep(randint(1,3))
            production_link = profile[:-15]
            production = get("https://www.imdb.com/" + production_link + "companycredits")
            production_html = BeautifulSoup(production.text, 'html.parser')
            comps_x = production_html.find("div", {"id": "company_credits_content"}).ul.findAll('a')
            for comp in comps_x:
                production_comps.append(comp.text)
            production_companies.append(production_comps)
            
            #Special Effects Companies            
            effects = get("https://www.imdb.com/{}companycredits".format(profile[:-15]))
            effects_html = BeautifulSoup(effects.text, 'html.parser')

            
            if effects_html.find("h4", {"id": "specialEffects"}):
                effects_comps = []
                comps_x = effects_html.find("h4", {"id": "specialEffects"}).findNext('ul').findAll('li')
                for comp in comps_x:
                    effects_comps.append(comp.a.text)
                spec_eff_comps.append(effects_comps)
            else:
                spec_eff_comps.append("null")
            #Director
            director = container.findAll('div')[3].findAll('p')[2].findAll('a')[0].text
            directors.append(director)


            synopsis_link = profile[:-15]
            sleep(randint(1,3))
            synopsis = get("https://www.imdb.com/" + synopsis_link + "plotsummary")
            synopsis_html = BeautifulSoup(synopsis.text, 'html.parser')

            plot_synopsis_content = synopsis_html.find("ul", {"id": "plot-synopsis-content"}).li.text
            plot_synopsis_content = plot_synopsis_content.strip()
            plot_synopsis.append(plot_synopsis_content)
            
            writers = []
            sleep(randint(1,3))
            credits = get("https://www.imdb.com/{}fullcredits".format(profile[:-15]))
            credits_html = BeautifulSoup(credits.text, 'html.parser')
            credit_containers = credits_html.find_all('table', class_ = 'simpleTable simpleCreditsTable')
            writers_x = credit_containers[1].tbody.findAll('tr')
            for writer in writers_x:
                if writer.find('td', attrs = {'colspan':'3'}):
                    1==1
                else:
                    answer = writer.find('td', class_ = 'name').text
                    writers.append(answer.strip())
            screen_writers.append(writers)
            
            
            #Metascore
            metascore = container.find('span', class_ = 'metascore')
            metascore = int(metascore.text)
            metascores.append(metascore)

            
            #Genre
            genre = container.p.find('span', class_ = 'genre').text.strip()
            genres.append(genre)
            
            if container.p.find('span', class_ = 'certificate') is not None:
                #MPAA rating
                mpaa = container.p.find('span', class_ = 'certificate').text
                mpaa_ratings.append(mpaa)
            else:
                na = "N/A"
                mpaa_ratings.append(na)
                
            #IMDb rating
            imdb = float(container.strong.text)
            imdb_ratings.append(imdb)
            
            try:
                #Gross
                bo_gross = container.findAll('div')[3].findAll('p')[3].findAll('span')[4]
                bo_gross = bo_gross['data-value']
                bo_gross = re.sub("[^\d\.]", "", bo_gross)
                gross.append(int(bo_gross))
            except:
                gross.append("null")
                
            comments = []
            reviews_link = profile[:-15]
            all_reviews = get("https://www.imdb.com/" + reviews_link + "reviews")
            html_reviews = BeautifulSoup(all_reviews.text, 'html.parser')
            num_reviews = int(html_reviews.find("div", {"id": "main"}).section.find('div', class_ = 'lister').span.text[:-8].replace(',', ''))
            math.ceil(num_reviews/25) -1

    
            driver = webdriver.Chrome("C:\\Users\Brian\Downloads\chromedriver\chromedriver.exe")
            driver.get("https://www.imdb.com/" + reviews_link + "reviews")
            sleep(randint(2,2))
            button = driver.find_element_by_id('load-more-trigger')
            try:
                for i in range(math.ceil(num_reviews/25) - 1):
                    button.click()
                    sleep(randint(1,1))

                src = driver.page_source
                parser = BeautifulSoup(src, 'lxml')
                list_of_attributes = {"class":"lister-item"}
                review_containers = parser.findAll("div", attrs=list_of_attributes)
                for container in review_containers:
                    comments.append(container.div.div.find("div", class_ = "content").div.text)
                movie_reviews.append(comments)
            except:
                movie_reviews.append('null')
            driver.close()
            
            #Trailer
            movie_name = name
            response = get("https://www.google.com/search?q={}+Trailer".format(movie_name.replace(" ", "+")))
            html_google = BeautifulSoup(response.text, 'html.parser')


            txt = html_google.find('div', class_='g').text
            x = re.findall("(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?",txt)
            link = "{}://{}{}".format(x[0][0], x[0][1], x[0][2])
            yt = pytube.YouTube(link)
            stream = yt.streams.first()
            os.mkdir("C:\\Users\Brian\Desktop\IMDb_Scrape\Movie_Trailers\{}".format(clean_filename(movie_name)))
            stream.download("C:\\Users\Brian\Desktop\IMDb_Scrape\Movie_Trailers\{}".format(clean_filename(movie_name)), "{}_trailer".format(clean_filename(movie_name)))
            
            #Key Frame Extraction
            def FrameCapture(path): 

                # Path to video file 
                vidObj = cv2.VideoCapture(path) 

                # Used as counter variable 
                count = 0

                # checks whether frames were extracted 
                success = 1

                while success: 
                    # vidObj object calls read 
                    # function extract frames 
                    success, image = vidObj.read() 

                    # Saves the frames with frame-count
                    if count % 2 == 0:
                        cv2.imwrite("C:\\Users\\Brian\\Desktop\\IMDb_Scrape\\Movie_Trailers\\{}\\frame%d.jpeg".format(clean_filename(movie_name)) % count, image) 

                    count += 1
            try:
                if __name__ == '__main__': 

                    # Calling the function 
                    FrameCapture("C:\\Users\\Brian\\Desktop\\IMDb_Scrape\\Movie_Trailers\\{}\\{}_trailer.mp4".format(clean_filename(movie_name), clean_filename(movie_name))) 
            except:
                key_frame_exception.append(clean_filename(movie_name))


# In[187]:


print("Names Length: {}".format(len(names)))
print("Length: {}".format(len(runtimes)))
print("Profile: {}".format(len(profile_pages)))
# print("Storyline: {}".format(len(storylines)))
print("Spe. Eff.: {}".format(len(spec_eff_comps)))
print("Date: {}".format(len(release_dates)))
print("Budget: {}".format(len(budgets)))
print("Synopsis: {}".format(len(plot_synopsis)))
print("Pro. Comp: {}".format(len(production_companies)))
print("Gross Length: {}".format(len(gross)))
print("Stars: {}".format(len(stars)))
print("Director Length: {}".format(len(directors)))
print("Screen Writers Length: {}".format(len(screen_writers)))
print("Metascore: {}".format(len(metascores)))
print("Genre: {}".format(len(genres)))
print("MPAA: {}".format(len(mpaa_ratings)))
print("IMDB: {}".format(len(imdb_ratings)))
# print("Awards: {}".format(len(movie_awards)))
print("Comments: {}".format(len(movie_reviews)))


# In[188]:


movie_ratings = pd.DataFrame({'movie': names,
                              'length': runtimes,
#                               'profile': profile_pages,
#                               'storyline': storylines,
                              'date': release_dates,
                              'budget': budgets,
                              'synopsis': plot_synopsis,
                              'pro. comp': production_companies,
                              'spec. eff': spec_eff_comps,
                                'gross': gross,
                              'stars': stars,
                        'director': directors,
                        'writer': screen_writers,
                             'metascore': metascores,
                              'genre': genres,
                              'mpaa': mpaa_ratings,
                              'imdb': imdb_ratings,
#                               'awards': movie_awards
                              'reviews': movie_reviews
                             })

print(movie_ratings.info())
movie_ratings.head(10)


# In[83]:


url = "https://www.imdb.com/title/tt1727824/companycredits"
response = get(url)

effects_html = BeautifulSoup(response.text, 'html.parser')

effects_comps = []
comps_x = effects_html.find("h4", {"id": "specialEffects"}).findNext('ul').findAll('li')
for comp in comps_x:
    effects_comps.append(comp.a.text)
effects_comps


# In[142]:


movie_name = "Alita: Battle Angel"
movie_year = "2019"
url_1 = "https://www.boxofficemojo.com/oscar/movies/?id={}.htm".format(movie_name.replace(" ", ""))
response_1 = get(url_1)
html_awards = BeautifulSoup(response_1.text, 'html.parser')
if html_awards.find("div", {"id": "body"}).h1.text not in [movie_name, "{} ({})".format(movie_name, movie_year)]:
    url_1 = "https://www.boxofficemojo.com/oscar/movies/?id={}{}.htm".format(movie_name.replace(" ", ""),movie_year)
    response_1 = get(url_1)
    html_awards = BeautifulSoup(response_1.text, 'html.parser')
    blah = []
    award_links = html_awards.find("div", {"id": "body"}).find_all('a')
    awards = {}
    for award in award_links:
        if "(WIN)" in award.text:
            link = "https://www.boxofficemojo.com/{}".format(award['href'])
            new_url = link
            new_response = get(link)
            html_award = BeautifulSoup(new_response.text, 'html.parser')
            html_award.find('font').extract()
            title = html_award.find('font').text
            if title == "BEST PICTURE":
                awards[title] = movie_name
            else:
                movie_name
                awards[title] = html_award.find(text="{} ({})".format(movie_name, movie_year)).findNext('font').text
else:
    award_links = html_awards.find("div", {"id": "body"}).find_all('a')
    awards = {}
    for award in award_links:
        if "(WIN)" in award.text:
            link = "https://www.boxofficemojo.com/{}".format(award['href'])
            new_url = link
            new_response = get(link)
            html_award = BeautifulSoup(new_response.text, 'html.parser')
            html_award.find('font').extract()
            title = html_award.find('font').text
            if title == "BEST PICTURE":
                awards[title] = movie_name
            else:
                awards[title] = html_award.find(text=movie_name).findNext('font').text
print(awards)


# In[184]:


comments = []


url = "https://www.imdb.com/title/tt7784604/reviews"
response = get(url)
html_reviews = BeautifulSoup(response.text, 'html.parser')
num_reviews = int(html_reviews.find("div", {"id": "main"}).section.find('div', class_ = 'lister').span.text[:-8].replace(',', ''))
math.ceil(num_reviews/25) -1


driver = webdriver.Chrome("C:\\Users\Brian\Downloads\chromedriver\chromedriver.exe")
driver.get("https://www.imdb.com/title/tt7784604/reviews")
button = driver.find_element_by_id('load-more-trigger')
for i in range(math.ceil(num_reviews/25) - 1):
    button.click()
    sleep(randint(1,1))
    
src = driver.page_source
parser = BeautifulSoup(src, 'lxml')
list_of_attributes = {"class":"lister-item"}
review_containers = parser.findAll("div", attrs=list_of_attributes)
for container in review_containers:
    comments.append(container.div.div.find("div", class_ = "content").div.text)
driver.close()


# In[185]:


comments[:10]


# In[17]:


import unicodedata
import unicode


# In[18]:





# In[22]:


clean_filename("asdf as df?")


# In[23]:


a = clean_filename("Deadpool 2")
a


# In[ ]:




