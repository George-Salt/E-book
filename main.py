import os
from urllib.error import HTTPError

import requests


URL = "http://tululu.org/txt.php?id={id}"


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
    os.makedirs("books", exist_ok=True)

    for book_num in range(10):
        check_for_redirect(URL, book_num, f"id{book_num}")
except HTTPError:
    print("Такой книги не существует!")
