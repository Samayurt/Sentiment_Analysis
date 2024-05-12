import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urlparse, urljoin
import re

def is_social_media_url(url):
    social_media_domains = ['twitter.com', 'facebook.com', 'instagram.com']  # Add more if needed
    for domain in social_media_domains:
        if domain in url:
            return True
    return False

def extract_all_links(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [a['href'] for a in soup.find_all('a', href=True)]
            links = [urljoin(url, link) for link in links]
            return links
        else:
            print(f"Failed to retrieve data from '{url}'. Status code: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to {url}: {e}")
        return []

def save_links_to_csv(links, csv_filename):
    with open(csv_filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Link'])  # Write header
        for link in links:
            csv_writer.writerow([link])

def extract_specific_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        if is_social_media_url(url):
            print(f"Skipping {url} because it's a social media link.")
            return None, None, None, None, url, 'Category not found'

        main_heading_div = soup.find('div', class_='main-heading')
        
        if main_heading_div:
            heading_element = main_heading_div.find('h2')
            author_element = soup.find('a', href=re.compile(r'/news/author/\d+'))
            publication_date_div = soup.find('div', class_='headline-time pull-left') 
            
            if publication_date_div:
                publication_date_raw = publication_date_div.find('p').get_text(strip=True)
                date_match = re.search(r'(\w+ \d{1,2}, \d{4} \d{2}:\d{2} [APap][Mm] [A-Z]+)', publication_date_raw)
                
                if date_match:
                    publication_date = date_match.group(1)
                else:
                    publication_date = 'Date not found'
            else:
                publication_date_raw = 'Date not found'
                publication_date = 'Date not found'
            
            content_container = soup.find('div', {'id': 'newsContent'})
            heading = heading_element.text.strip() if heading_element else 'Heading not found'
            author = author_element.text.strip() if author_element else 'Author not found'
            category = 'Category not found'
            url_parts = urlparse(url).path.split('/')
            if url_parts[1]:
                category = url_parts[1]

            content = content_container.get_text(separator=' ', strip=True) if content_container else 'Content not found'
            content = re.sub(rf'{re.escape(heading)}.*?{re.escape(publication_date)}', '', content).strip()

            return heading, author, publication_date, content, url, category
        else:
            print(f"Main heading div not found on {url}.")
            return None, None, None, None, url, 'Category not found'

    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve content from {url}. Error: {e}")
        return None, None, None, None, url, 'Category not found'

def save_to_csv(data, csv_file_path):
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Heading', 'Author', 'Publication_date', 'Content', 'Link', 'Category'])
        csv_writer.writerow(data)

def main():
    csv_file_path = 'Republica_data.csv'
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Heading', 'Author', 'Publication_date', 'Content', 'Link', 'Category'])

    url = 'https://myrepublica.nagariknetwork.com/'
    links = extract_all_links(url)
    csv_filename = 'Republica_links.csv'
    save_links_to_csv(links, csv_filename)

    with open(csv_filename, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        urls = [row['Link'] for row in reader]

    for url in urls:
        if not urlparse(url).scheme:
            url = urljoin('https://', url)

        if urlparse(url).netloc and not is_social_media_url(url):
            heading, author, publication_date, content, link, category = extract_specific_content(url)
            if heading is not None and author is not None and content is not None:
                data_to_save = [heading, author, publication_date, content, link, category]
                print(f"Data for {url}:\nHeading: {heading}\nAuthor: {author}\nPublication Date: {publication_date}\nSource: Republica\nContent: {content}\nLink: {link}\nCategory: {category}\n")
                save_to_csv(data_to_save, csv_file_path)
                print(f"Data saved for {url}")
        else:
            print(f"Invalid URL format or social media link: {url}")

if __name__ == "__main__":
    main()






