import argparse
import os
from urllib.error import HTTPError
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def parse_book_page(id, book_url, template_url):
    response = requests.get(book_url.format(id=id))
    page_code = BeautifulSoup(response.text, "lxml")

    book_name = page_code.find("h1").text.split(" :: ")[0].strip()

    author_name = page_code.find("h1").text.split(" :: ")[1].strip()

    img_url = page_code.find("div", class_="bookimage").find("img")["src"]
    full_img_url = urljoin(template_url, img_url)

    book_genres = []
    book_genre_tags = page_code.find("span", class_="d_book").find_all("a")
    for genre_tag in book_genre_tags:
        book_genres.append(genre_tag.text)

    comments = page_code.find_all("div", class_="texts")
    comments_texts = []
    for comment in comments:
        comment_text = comment.find("span", class_="black").text
        comments_texts.append(comment_text)

    book_parameters = {
        "Название": book_name,
        "Автор": author_name,
        "Ссылка на картинку": full_img_url,
        "Жанр": book_genres,
        "Комментарии": comments_texts
    }
    return book_parameters


def check_for_redirect(url, id, book_url, template_url):
    response = requests.get(url.format(id=id))
    if not response.history == []:
        response.raise_for_status()
    else:
        print(download_image(parse_book_page(id, book_url, template_url)["Ссылка на картинку"]))
        print(download_txt(response, parse_book_page(id, book_url, template_url)["Название"]))
        print(parse_book_page(id, book_url, template_url))


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Программа скачивает книги, картинки к ним и выводит описание книги."
    )
    parser.add_argument("--start_id", type=int, help="С какой книги скачать", default=1)
    parser.add_argument("--end_id", type=int, help="До какой книги скачать", default=10)
    args = parser.parse_args()

    template_img_url = "http://tululu.org/images/nopic.gif"
    download_url = "http://tululu.org/txt.php?id={id}"
    book_url = "http://tululu.org/b{id}/"

    try:
        os.makedirs("images", exist_ok = True)
        os.makedirs("books", exist_ok = True)

        for book_num in range(args.start_id, args.end_id):
            check_for_redirect(download_url, book_num, book_url, template_img_url)
    except HTTPError:
        print("Такой книги не существует!")
