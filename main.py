import os

import requests


os.makedirs("books", exist_ok=True)


def download_book(id, name):
    url = f"http://tululu.org/txt.php?id={id}"

    response = requests.get(url)
    response.raise_for_status() 

    filepath = f"books/{name}.txt"
    with open(filepath, "wb") as file:
        file.write(response.content)
    return f"Скачано в {filepath}"


for book_num in range(10):
    download_book(book_num, f"id{book_num}")
