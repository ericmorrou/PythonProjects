import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame

base_url = "https://books.toscrape.com/catalogue/page-{}.html"

# Creamos los arrays para guardar la info obtenida
titles = []
prices = []
ratings = []
availability = []
links = []

for page in range(1, 11):
    url = base_url.format(page)
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    books = soup.find_all("article", class_="product_pod")

    for book in books:
        title = book.h3.a["title"]

        price_text = book.find("p", class_="price_color").text
        price_clean = price_text.replace("£", "").replace("Â", "")
        price = float(price_clean)

        rating = book.p["class"][1]
        avail = book.find("p", class_="instock availability").text.strip()
        link = "https://books.toscrape.com/catalogue/" + book.h3.a["href"]

        titles.append(title)
        prices.append(price)
        ratings.append(rating)
        availability.append(avail)
        links.append(link)

df = pd.DataFrame({
    "Titulo": titles,
    "Precio": prices,
    "Rating": ratings,
    "Disponibilidad": availability,
    "Enlaces": links
})

df.to_csv("data.csv")
