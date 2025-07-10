import requests
from bs4 import BeautifulSoup

url = "https://www.junglelodges.com/resort/kabini-river-lodge/"
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    all_text = ""

    # Get the title
    title = soup.find("h1")
    if title:
        all_text += f"Title: {title.text.strip()}\n\n"

    # Get main package sections
    packages = soup.find_all("div", class_="package-block")
    for pkg in packages:
        name = pkg.find("h3").text.strip() if pkg.find("h3") else "No package name"
        price = pkg.find("span", class_="price").text.strip() if pkg.find("span", class_="price") else "No price"
        details = pkg.find("div", class_="package-details").text.strip() if pkg.find("div", class_="package-details") else "No details"
        
        all_text += f"Package: {name}\nPrice: {price}\nDetails: {details}\n\n"

    # Save to data.txt
    with open("data.txt", "w", encoding="utf-8") as f:
        f.write(all_text)

    print("Data saved to data.txt")
else:
    print(" Failed to fetch page. Status code:", response.status_code)
