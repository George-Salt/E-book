import os
from urllib.error import HTTPError
from urllib.parse import unquote
from urllib.parse import urljoin
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


template_img_url = "http://tululu.org/images/nopic.gif"
URL = "http://tululu.org/txt.php?id={id}"
book_url = "http://tululu.org/b{id}/"


def get_book_name(id, book_url):
    response = requests.get(book_url.format(id=id))

    soup = BeautifulSoup(response.text, "lxml")

    title_tag = soup.find("h1")
    book_name = title_tag.text.split(" :: ")[0].strip()
    return book_name


def get_book_img_url(id, book_url, template_url):
    response = requests.get(book_url.format(id=id))
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    soup.unicode

    img_url = soup.find("div", class_="bookimage").find("img")["src"]
    full_img_url = urljoin(template_url, img_url)
    return full_img_url


def check_for_redirect(url, id, book_url, main_url):
    response = requests.get(url.format(id=id))
    if not response.history == []:
        response.raise_for_status()
    else:
        print(download_image(get_book_img_url(id, book_url, main_url)))
        print(download_txt(response, get_book_name(id, book_url)))


def download_image(img_url, folder = "images/"):
    response = requests.get(img_url)

    filename = urlsplit(img_url).path.split("/")[-1]
    filepath = os.path.join(folder, filename)
    with open(unquote(filepath), "wb") as file:
        file.write(response.content)
    return f"Картинка: {filepath}"


def download_txt(response, filename, folder = "books/"):
    filepath = os.path.join(folder, f"{sanitize_filename(filename)}.txt")
    with open(filepath, "wb") as file:
        file.write(response.content)
    return f"Книга: {filepath}"


try:
    os.makedirs("images", exist_ok = True)
    os.makedirs("books", exist_ok = True)

    for book_num in range(10):
        check_for_redirect(URL, book_num, book_url, template_img_url)
except HTTPError:
    print("Такой книги не существует!")
