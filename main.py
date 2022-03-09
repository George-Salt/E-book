import os
from urllib.error import HTTPError

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


main_url = "http://tululu.org"
URL = "http://tululu.org/txt.php?id={id}"
book_url = "http://tululu.org/b{id}/"


def get_book_name(id, book_url):
    response = requests.get(book_url.format(id=id))

    soup = BeautifulSoup(response.text, "lxml")

    title_tag = soup.find("h1")
    book_name = title_tag.text.split(" :: ")[0].strip()
    return book_name


def get_book_author(response):
    soup = BeautifulSoup(response.text, "lxml")

    title_tag = soup.find("h1")
    author = title_tag.text.split(" :: ")[1].strip()
    return author


def get_book_img_url(response, main_url):
    soup = BeautifulSoup(response.text, "lxml")

    if soup.find(class_="bookimage").find("a").find("img")["src"] == True:
        img_url = soup.find(class_="bookimage").find("a").find("img")["src"]
        full_img_url = f"{main_url}{img_url}"
    return full_img_url


def check_for_redirect(url, id, book_url):
    response = requests.get(url.format(id=id))
    if not response.history == []:
        response.raise_for_status()
    else:
        download_txt(response, get_book_name(id, book_url))


def download_txt(response, filename, folder = 'books/'):
    filepath = os.path.join(folder, f"{sanitize_filename(filename)}.txt")
    with open(filepath, "wb") as file:
        file.write(response.content)
    return f"Скачано в {filepath}"


try:
    os.makedirs("books", exist_ok = True)

    for book_num in range(10):
        check_for_redirect(URL, book_num, book_url)
except HTTPError:
    print("Такой книги не существует!")
