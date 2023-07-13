import sqlite3
import argparse
import csv
import os
from website_metadata.main import Metadata
from report import generate_report

default_table = """CREATE TABLE IF NOT EXISTS websites(id integer PRIMARY KEY, url text NOT NULL, title text, category text, language text, headers text, content text, favicon text, robots text, humans text, sitemap text, status text)"""

def main():
    parser = argparse.ArgumentParser(description="Get site data")
    parser.add_argument("-u", "--url", type=str, help="Url of site to retrieve data from")
    parser.add_argument("-l", "--list", type=str, help="List of urls to retrieve data from")
    parser.add_argument("-f", "--folder", type=str, default="data", help="Folder to store data (favicons) in")
    parser.add_argument("-r", "--report", action="store_true", help="Generate report")
    parser.add_argument("--dry-run", action="store_true", help="Fetch data but do not save to database")
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(default_table)

    if parser.parse_args().list:
        with open(parser.parse_args().list) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                print(row[0])
                meta = Metadata(row[0])
                if not parser.parse_args().dry_run:
                    add_to_db(cur, con, meta, row[1])
                    download_favicon(parser.parse_args().folder, meta)
                else:
                    print(meta.language)
    elif parser.parse_args().url:
        print(parser.parse_args().url)
        meta = Metadata(parser.parse_args().url)
        print(meta.status)
        if not parser.parse_args().dry_run:
            add_to_db(cur, con, meta, "test")
            download_favicon(parser.parse_args().folder, meta)
        else:
            print(meta.language)
    elif parser.parse_args().report:
        generate_report(cur, con)
    else:
        parser.print_help()

    con.close()


def add_to_db(cur, con, metadata, category):
    cur.execute("INSERT INTO websites(url, title, category, language, headers, content, favicon, robots, humans, sitemap, status) VALUES(?,?,?,?,?,?,?,?,?,?,?)", 
                    (metadata.url, metadata.title, category, metadata.language, str(metadata.raw_respheader), str(metadata.raw_html), str(metadata.best_icon()), metadata.robots, metadata.humans, metadata.sitemap, metadata.status))
    con.commit()

def download_favicon(dir, metadata):
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    if metadata.best_icon():
        metadata.best_icon().save(dir)


if __name__ == "__main__":
    main()