import os
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import requests


main_url = "http://tululu.org"
URL = "http://tululu.org/txt.php?id={id}"
book_url = "http://tululu.org/b{id}/"


def get_book_parameters(url, id, main_url):
    response = requests.get(url.format(id=id))
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    title_tag = soup.find("h1")
    book_name = title_tag.text.split(" :: ")[0].strip()
    author = title_tag.text.split(" :: ")[1].strip()

    img_url = soup.find(class_="bookimage").find("a").find("img")["src"]
    return f"Заголовок: {book_name}.\nАвтор: {author}. \nСсылка на картинку: {main_url}{img_url}."


def check_for_redirect(url, id, name):
    response = requests.get(url.format(id=id))
    if not response.history == []:
        response.raise_for_status()
    else:
        download_book(response, name)


def download_book(response, name):
    filepath = f"books/{name}.txt"
    with open(filepath, "wb") as file:
        file.write(response.content)
    return f"Скачано в {filepath}"


try:
    print(get_book_name_and_author(book_url, 298, main_url))

    os.makedirs("books", exist_ok=True)

    for book_num in range(10):
        check_for_redirect(URL, book_num, f"id{book_num}")
except HTTPError:
    print("Такой книги не существует!")
