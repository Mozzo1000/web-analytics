from jinja2 import Environment, FileSystemLoader

def generate_report(cur, con):
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("report.html")
    filename = "results.html"
    urls = []
    status = []
    cur.execute("SELECT url FROM websites")
    rows = cur.fetchall()
    for row in rows:
        urls.append(row[0])

    cur.execute("SELECT status, COUNT(status) FROM websites GROUP BY status")
    rows = cur.fetchall()
    for row in rows:
        status.append(row)

    with open(filename, mode="w", encoding="utf-8") as results:
        results.write(template.render({"url": urls, "status": status}))
        print(f"wrote {filename}")