import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import pandas as pd


def is_internal_link(base_url, link):
    # Check if the link is internal to the base_url domain
    base_domain = urlparse(base_url).netloc
    link_domain = urlparse(link).netloc

    return base_domain == link_domain

def extract_all_links(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract all links using BeautifulSoup methods
            links = [a['href'] for a in soup.find_all('a', href=True)]

            # Convert relative URLs to absolute URLs
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
        csv_writer.writerow(['Link', 'Type'])  # Write header

        for link in links:
            link_type = 'Internal' if is_internal_link(url, link) else 'External'
            csv_writer.writerow([link, link_type])

# Specify the URL
url = 'https://en.setopati.com/'

# Extract all links from the specified URL
links = extract_all_links(url)

# Save links to CSV file with their types (Internal or External)
csv_filename = 'data_links.csv'
save_links_to_csv(links, csv_filename)

# Print a message indicating success
print(f"All links saved to {csv_filename}")

link=pd.read_csv('data_links.csv')

def is_social_media_url(url):
    social_media_domains = ['twitter.com', 'facebook.com', 'instagram.com']  # Add more if needed
    for domain in social_media_domains:
        if domain in url:
            return True
    return False

def extract_specific_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Skip extraction for social media URLs
        if is_social_media_url(url):
            print(f"Skipping {url} because it's a social media link.")
            return None, None, None, None, None  # Include the original link as None

        heading_element = soup.find('span', class_='news-big-title')
        author_element = soup.find('h2', class_='main-title')
        publication_date_element = soup.find('div', class_='published-date col-md-6')  # Corrected variable name
        content_container = soup.find('div', class_='editor-box')

        # Determine category based on the last part of the URL
        url_parts = urlparse(url).path.split('/')
        last_url_part = url_parts[-1]
        if last_url_part.isnumeric() and len(url_parts) > 1:
            category = url_parts[-2]
        else:
            category = last_url_part

        heading = heading_element.text.strip() if heading_element else 'Heading not found'
        author = author_element.text.strip() if author_element else 'Author not found'
        publication_date_raw = publication_date_element.text.strip() if publication_date_element else 'Date not found'  # Corrected variable name
        # Remove the unwanted prefix "प्रकाशित :"
        publication_date = publication_date_raw.replace('Published Date:', '').strip()
        content = content_container.get_text(separator=' ', strip=True) if content_container else 'Content not found'

        return heading, author, publication_date, content, url, category  # Include the original link and category
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve content from {url}. Error: {e}")
        return None, None, None, None, url, None  # Include the original link and None for category

def save_to_csv(data, csv_file_path):
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Heading', 'Author', 'Publication_date', 'Source', 'Content', 'Link', 'Category'])  # Updated header
        csv_writer.writerow(data)  # Added 'ekantipur' as the source

def main():
    csv_file_path = 'setopati.csv'

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Heading', 'Author', 'Publication_date','Source','Content' ,'Link', 'Category'])  # Updated header

    with open('data_links.csv', 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        urls = [row['Link'] for row in reader]

    for url in urls:
        if not urlparse(url).scheme:
            url = urljoin('https://', url)

        if urlparse(url).netloc and not is_social_media_url(url):
            heading, author, publication_date, content, link, category = extract_specific_content(url)
            if heading is not None and author is not None and content is not None:
                data_to_save = [heading, author, publication_date,'Seto_Pati',content, link, category]
                print(f"Data for {url}:\nHeading: {heading}\nAuthor: {author}\nPublication Date: {publication_date}\nSource: Seto_Pati\nContent: {content}\nLink: {link}\nCategory: {category}\n")
                save_to_csv(data_to_save, csv_file_path)
                print(f"Data saved for {url}")
        else:
            print(f"Invalid URL format or social media link: {url}")

if __name__ == "__main__":
    main()
