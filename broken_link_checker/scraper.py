import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from optparse import OptionParser


def fetch_all_sitemap_links(sitemap):
    user_agent = {"User-agent": "Mozilla/5.0"}
    r = requests.get(sitemap, headers=user_agent)
    soup = BeautifulSoup(r.text, features="html.parser")

    links = [link.text for link in soup.find_all("loc")]
    recursive_links = []
    print("Fetching sitemap : {}".format(sitemap))
    for link in links:
        if link.endswith(".xml") or "/blog/sitemap" in link:
            new_links = fetch_all_sitemap_links(link)
            recursive_links.append(new_links)
        else:
            recursive_links.append(link)
    links = list(set(links + [x for y in recursive_links for x in y]))
    return links


def crawl_link(link):
    if len(link) < 3:
        ## Sometimes the sitemaps contains random characters and we can exclude them
        ## from crawling
        return []
    print("Crawling : {}".format(link))
    user_agent = {"User-agent": "Mozilla/5.0"}
    r = requests.get(link, headers=user_agent)
    soup = BeautifulSoup(r.text, features="lxml")
    links = []
    for a in soup.find_all("a", href=True):
        # print("Found the URL:", a["href"])
        if a["href"].startswith("http"):
            links.append((link, a["href"]))
    return links


def check_link_status(link):
    user_agent = {"User-agent": "Mozilla/5.0"}
    r = requests.get(link[1], headers=user_agent)
    broken = r.status_code == 404
    return (link[0], link[1], broken)


def run_link_checker(sitemap):
    URLS = fetch_all_sitemap_links(sitemap)

    links_to_check = []
    # We can use a with statement to ensure threads are cleaned up promptly
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(crawl_link, url): url for url in URLS}

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print("%r generated an exception: %s" % (url, exc))
            links_to_check.append(data)

    unique_links_to_check = list(set([x for y in links_to_check for x in y]))
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(check_link_status, url): url for url in unique_links_to_check}

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            status = False
            try:
                parent_link, broken_link, status = future.result()
            except Exception as exc:
                print("%r generated an exception: %s" % (url, exc))
            if status:
                print("Broken Link : {} on page : {}".format(broken_link, parent_link))


parser = OptionParser()
parser.add_option("-s", "--sitemap", dest="sitemap", help="Provide the link to the sitemap")
parser.add_option(
    "-q",
    "--quiet",
    action="store_false",
    dest="verbose",
    default=True,
    help="don't print status messages to stdout",
)

(options, args) = parser.parse_args()
run_link_checker    (options.sitemap)
