import requests
import csv
import os

# Replace these with your values
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_OWNER = "gdsfactory"
REPO_NAME = "gdsfactory"

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def get_contributors():
    contributors = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contributors"
        response = requests.get(url, headers=HEADERS, params={"per_page": 100, "page": page})
        data = response.json()
        if not data or response.status_code != 200:
            break
        contributors.extend(data)
        page += 1
    return contributors

def get_user_name(login):
    url = f"https://api.github.com/users/{login}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return login, "", ""
    profile = response.json()
    full_name = profile.get("name") or ""
    first, last = "", ""
    if full_name:
        parts = full_name.strip().split()
        if len(parts) == 1:
            first = parts[0]
        elif len(parts) > 1:
            first = parts[0]
            last = " ".join(parts[1:])
    return login, first, last

def main():
    contributors = get_contributors()
    with open("contributors.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["username", "first_name", "last_name"])
        for contributor in contributors:
            login = contributor["login"]
            username, first_name, last_name = get_user_name(login)
            writer.writerow([username, first_name, last_name])
    print("✅ contributors.csv has been created.")

if __name__ == "__main__":
    main()