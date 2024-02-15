from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import os


# GET THE DELAY TIME FROM ROBOTS.TXT
url = "https://pureportal.coventry.ac.uk/robots.txt/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
soup = str(soup)
delay_time = int(soup.split('Crawl-Delay:')[-1].split('\n')[0].strip())

# OPENING THE SITE
url = "https://pureportal.coventry.ac.uk/en/organisations/ihw-centre-for-health-and-life-sciences-chls/publications/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
time.sleep(delay_time)

# CREATING PUBLICATION_TITLES.TXT FILE TO SAVE TITLES
if not os.path.exists('publication_titles.txt'):
    with open('publication_titles.txt', 'w', encoding='utf-8') as f:
        pass

details = []

# GETTING ALL THE RESULTS
result_tag = soup.find('ul', class_='list-results')
if result_tag:
    results = result_tag.find_all('li')
    for result in results:
        publication_tag = result.find('h3', class_='title')
        if publication_tag:
            publication = publication_tag.find('a', class_='link')
            title = publication.text.strip()

            # READING THE PUBLICATION_TITLES.TXT FILE TO CHECK EITHER THAT TITLE IS ALREADY PRESENT THERE OR NOT
            with open('publication_titles.txt', 'r', encoding='utf-8') as f:
                reader = f.read()
                reader = reader.split('\n')
            
            # IF TITLE IS NOT PRESENT THERE THEN SCRAPE TITLE AND LINK
            if title not in reader:            
                link = publication['href']
                detail = {
                    'Title': title,
                    'Publication Url': link
                }
                details.append(detail)

# VISIT EACH PUBLICATION LINK ONE BY ONE
if len(details) > 0:
    for l in range(len(details)):
        link = details[l]['Publication Url']
        title = details[l]['Title']
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
    
        # SCRAPING AUTHOR NAMES
        author_tag = soup.find('p', class_='persons')
        if author_tag:
            authors = author_tag.text.strip()
        else:
            authors = ''

        details[l]['Authors'] = authors

        # SCRAPING AUTHOR LINK
        author_link = soup.find('a', rel='Person')
        if author_link:
            author_link = author_link['href']
        else:
            author_link = ''
            
        details[l]['Profile Url'] = author_link
    
        # SCRAPING ORGANISATION
        research_list = []
        research_tag = soup.find('ul', class_='organisations')
        if research_tag:
            researches = research_tag.find_all('li')
            for r in researches:
                research_list.append(r.text)
            
            researches = ", ".join(research_list)
        else:
            researches = ''
    
        details[l]['Organisation'] = researches
        
        # SCRAPING DATE OF PUBLISHED
        published_date_tag = soup.find('table', class_='properties')
        if published_date_tag:
            published_date = published_date_tag.find_all('span', class_='date')
            if published_date:
                published_date = published_date[-1].text.strip()
        else:
            published_date = ''
    
        details[l]['Year'] = published_date
            
        # SCRAPING JOURNAL
        journal_tag = soup.find('a', rel='Journal')
        if journal_tag:
            journal = journal_tag.find('span')
            if journal:
                journal = journal.text.strip()
        else:
            journal = ""
    
        details[l]['Journal'] = journal

        # AFTER SCRAPING ALL THE DETAILS OF THE TITLE, TITLE IS BEING SAVED IN THE PUBLICATION_TITLES.TXT FILE
        with open('publication_titles.txt', 'a', encoding='utf-8') as f:
            f.write(f'{title}\n')
        
        print(l)
        
        time.sleep(delay_time)


# CHECKING IF PUBLICATIONS.XLSX FILE NOT PRESENT THERE THEN CREATE IT
if not os.path.exists('publications.xlsx'):
    with open('publications.xlsx', 'w') as f:
        pass

# READING THE EXISTING DATA
try:
    existing_data = pd.read_excel('publications.xlsx')
except:
    pass

# READING NEW SCRAPED DATA
new_data = pd.DataFrame(details)

# COMBINED EXISTING DATA + NEW DATA
try:
    new_data = pd.concat([existing_data, new_data], ignore_index=True)
except:
    pass

# REMOVING DUPLICATES
new_data = new_data.drop_duplicates(subset='Title')

# SAVING THE DATA IN THE PUBLICATIONS.XLSX FILE
new_data.to_excel('publications.xlsx', index=False)