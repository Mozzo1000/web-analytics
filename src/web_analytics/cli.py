import sqlite3
import argparse
import csv
from website_metadata.main import Metadata
from report import generate_report

default_table = """CREATE TABLE IF NOT EXISTS websites(id integer PRIMARY KEY, url text NOT NULL, title text, category text, headers text, content text, favicon text, robots text, humans text, sitemap text, status text)"""

def main():
    parser = argparse.ArgumentParser(description="Get site data")
    parser.add_argument("-u", "--url", type=str, help="Url of site to retrieve data from")
    parser.add_argument("-l", "--list", type=str, help="List of urls to retrieve data from")
    parser.add_argument("-f", "--folder", type=str, default="data", help="Folder to store data (favicons) in")
    parser.add_argument("-r", "--report", action="store_true", help="Generate report")

    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute(default_table)

    if parser.parse_args().list:
        with open(parser.parse_args().list) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                print(row[0])
                meta = Metadata(row[0])
                add_to_db(cur, con, meta, row[1])

    elif parser.parse_args().url:
        print(parser.parse_args().url)
        meta = Metadata(parser.parse_args().url)
        print(meta)
        add_to_db(cur, con, meta, "test")
        #get_site_data(parser.parse_args().url, cur, con, parser)
    elif parser.parse_args().report:
        generate_report(cur, con)
    else:
        parser.print_help()

    con.close()


def add_to_db(cur, con, metadata, category):
    cur.execute("INSERT INTO websites(url, title, category, headers, content, favicon, robots, humans, sitemap, status) VALUES(?,?,?,?,?,?,?,?,?,?)", 
                    (metadata.url, metadata.title, category, str(metadata.raw_respheader), str(metadata.raw_html), str(metadata.best_icon()), metadata.robots, metadata.humans, metadata.sitemap, metadata.status))
    con.commit()

if __name__ == "__main__":
    main()