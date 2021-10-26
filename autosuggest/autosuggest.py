import requests  # Include functionality to make a call to the remote websites
import pandas as pd

urls = {
    "google": "https://suggestqueries.google.com/complete/search?client=chrome&q=",
    "amazon": "https://completion.amazon.com/search/complete?search-alias=aps&client=amazon-search-ui&mkt=1&q=",
    "youtube": "http://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q=",
}

df_queries = pd.read_csv("queries.csv")
# queries.csv will look like below
# queries (header)
# jewelry
# kids school
# search engine optimization

queries = df_queries.queries

to_be_saved_queries = []
all_autosuggestions = []
domains = []
for query in queries:
    for (domain, url) in urls.items():
        # add the query to the url
        remote_url = url + query
        print(f"Remote url : {remote_url}")
        response = requests.get(remote_url).json()
        auto_suggest = response[1]
        print(auto_suggest)
        for suggestion in auto_suggest:
            to_be_saved_queries.append(query)
            all_autosuggestions.append(suggestion)
            domains.append(domain)

df = pd.DataFrame({"domain": domains, "query": to_be_saved_queries, "autosuggestions": all_autosuggestions})
df.to_csv("autosuggestion.csv", index=False)