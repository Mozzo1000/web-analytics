from jinja2 import Environment, FileSystemLoader
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas

def generate_report(cur, con):
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("report.html")
    filename = "results.html"
    urls = []
    cur.execute("SELECT url FROM websites")
    rows = cur.fetchall()
    for row in rows:
        urls.append(row[0])
    
    cur.execute("SELECT url, title, category, status FROM websites")
    all_data = cur.fetchall()


    sql = "SELECT status, COUNT(status) as c_status FROM websites GROUP BY status"
    status_data = pandas.read_sql(sql, con)

    fig, ax = plt.subplots()
    bar_container = ax.bar(status_data.status, status_data.c_status, color=['blue', 'red', 'green'])
    plt.title("Status codes")

    plt.xlabel("HTTP status codes")
    plt.ylabel("Occurrence of code")
    ax.bar_label(bar_container)

    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png')
    encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

    with open(filename, mode="w", encoding="utf-8") as results:
        results.write(template.render({"all_data": all_data, "url": urls, "image_1": encoded}))
        print(f"wrote {filename}")