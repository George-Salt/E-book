import argparse
import os

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import unquote, urljoin, urlsplit


def parse_book_page(id, book_url, template_url):
    response = requests.get(book_url.format(id=id))
    response.raise_for_status()
    page_code = BeautifulSoup(response.text, "lxml")

    header_tag = page_code.find("h1").text
    book_name, author_name = header_tag.split(" :: ")

    img_url = page_code.find("div", class_="bookimage").find("img")["src"]
    full_img_url = urljoin(template_url, img_url)

    book_genre_tags = page_code.find("span", class_="d_book").find_all("a")
    book_genres = [genre_tag.text for genre_tag in book_genre_tags]

    comments = page_code.find_all("div", class_="texts")
    comments_texts = [comment.find("span", class_="black").text for comment in comments]

    book_parameters = {
        "Название": book_name.strip(),
        "Автор": author_name.strip(),
        "Ссылка на картинку": full_img_url,
        "Жанр": book_genres,
        "Комментарии": comments_texts
    }
    return book_parameters


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_image(img_url, folder = "images/"):
    response = requests.get(img_url)
    response.raise_for_status()

    filename = urlsplit(img_url).path.split("/")[-1]
    filepath = os.path.join(folder, filename)
    with open(unquote(filepath), "wb") as file:
        file.write(response.content)
    return f"Картинка: {filepath}"


def save_book(response, filename, folder = "books/"):
    filepath = os.path.join(folder, f"{sanitize_filename(filename)}.txt")
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(response.text)
    return f"Книга: {filepath}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Программа скачивает книги, картинки к ним и выводит описание книги."
    )
    parser.add_argument("--start_id", type=int, help="С какой книги скачать", default=1)
    parser.add_argument("--end_id", type=int, help="До какой книги скачать", default=10)
    args = parser.parse_args()

    template_img_url = "http://tululu.org/images/nopic.gif"
    download_url = "https://tululu.org/txt.php"
    book_url = "https://tululu.org/b{id}/"

    os.makedirs("images", exist_ok = True)
    os.makedirs("books", exist_ok = True)
    for book_num in range(args.start_id, args.end_id):
        params = {"id": book_num}
        response = requests.get(download_url, params)
        try:
            response.raise_for_status()
            check_for_redirect(response)
            book_page = parse_book_page(book_num, book_url, template_img_url)
            print(
                save_book(response, book_page["Название"]),
                download_image(book_page["Ссылка на картинку"]),
                book_page
            )
        except requests.exceptions.HTTPError:
            print("Книги не существует")
