import argparse
import sqlite3
import requests
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
import os
import csv

# What data we want to retrieve and store for analysis : 
# URL
# Title
# Raw html content
# Favicon (save the image)
# robots.txt
# humans.txt
# sitemap.xml
# headers

default_table = """CREATE TABLE IF NOT EXISTS sites(id integer PRIMARY KEY, url text NOT NULL, title text, category text, headers text, content text, favicon text, robots text, humans text, sitemap text)"""

user_agent_header = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"

def main():
    parser = argparse.ArgumentParser(description="Get site data")
    parser.add_argument("-u", "--url", type=str, help="Url of site to retrieve data from")
    parser.add_argument("-l", "--list", type=str, help="List of urls to retrieve data from")
    parser.add_argument("-f", "--folder", type=str, default="data", help="Folder to store data (favicons) in")

    if not os.path.exists(parser.parse_args().folder):
        os.mkdir(parser.parse_args().folder)

    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(default_table)

    if parser.parse_args().list:
        with open(parser.parse_args().list) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                print(row[0])
                get_site_data(row[0], row[1], cur, con, parser)

    elif parser.parse_args().url:
        get_site_data(parser.parse_args().url, cur, con, parser)
    else:
        parser.print_help()

    con.close()

def get_site_data(url, category, cur, con, parser):
    response = requests.get(url, headers={"User-Agent": user_agent_header})
    #print(response.text)
    if response.status_code == 200:
        url = url
        content = response.text
        headers = str(response.headers)
        title = get_title(content)
        icon = get_icon(url, content, parser.parse_args().folder)
        robots = get_robots(url)
        humans = get_humans(url)
        sitemap = get_sitemap(url)

        cur.execute("INSERT INTO sites(url, title, category, headers, content, favicon, robots, humans, sitemap) VALUES(?,?,?,?,?,?,?,?,?)", 
                    (url, title, category, headers, content, icon, robots, humans, sitemap))
        con.commit()

    else:
        print(f"Failed to load site {parser.parse_args().url}")


def get_title(html):
    soup = BeautifulSoup(html, 'html.parser')
    try: 
        title = soup.find("title").get_text()
    except AttributeError:
        title = None
    return title

def get_icon(url, html, folder):

    soup = BeautifulSoup(html, 'html.parser')
    try: 
        icon_link = soup.find("link", rel="icon")["href"]
    except:
        icon_link = "favicon.ico"

    try: 
        req = requests.get(icon_link, stream=True)
    except requests.exceptions.MissingSchema:
        req = requests.get(urljoin(url, icon_link), stream=True)

    if req.status_code == 200:
        path = os.path.join(folder, urlsplit(url).netloc)
        if not os.path.exists(path):
            os.mkdir(path)
        with open(os.path.join(path, icon_link.replace("/","")), "wb") as f:
            for chunk in req:
                f.write(chunk)
        return path + icon_link

    return None 

def get_robots(url):
    url = urljoin(url, "robots.txt")
    req = requests.get(url)
    if req.status_code == 200:
        return req.text
    return None

def get_humans(url):
    url = urljoin(url, "humans.txt")
    req = requests.get(url)
    if req.status_code == 200:
        return req.text
    return None
    
def get_sitemap(url):
    url = urljoin(url, "sitemap.xml")
    req = requests.get(url)
    if req.status_code == 200:
        return req.text
    return None

if __name__ == "__main__":
    main()