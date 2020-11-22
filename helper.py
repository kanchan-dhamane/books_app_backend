from services.db_service import DbService
from queries import *
from config import (VALID_QUERY_PARAMS,
                    PAGE_SIZE,
                    BASE_URL)

filter_query_map = {
    "languages": BOOK_IDS_BY_LANGUAGE,
    "mime_type": BOOK_IDS_BY_MIME_TYPE,
    "author": BOOK_IDS_BY_AUTHOR,
    "title": BOOK_IDS_BY_TITLE,
    "topic": BOOK_IDS_BY_TOPIC,
    "search": BOOK_ID_BY_AUTHOR_AND_TITLE
}

# VALID_QUERY_PARAMS = ["ids", "author", "title", "topic", "languages", "mime_type", "page"]
# PAGE_SIZE = 25
# BASE_URL = "http://0.0.0.0:5000/books"


def handle_request(request):
    page = 1
    book_ids = set()
    filters = list(request.args.keys())
    for key in filters:
        value = request.args.get(key)
        print("{}: {}".format(key, value))

        if key == "page":
            page = int(value)
            continue

        if key == "ids":
            ids = set(value.split(","))
            book_ids = ids if not book_ids else book_ids.intersection(ids)
            continue

        f_key, f_value = get_filter_key_value(key, value)
        query = filter_query_map[f_key].format(*f_value)

        if book_ids:
            query += BOOK_FILTER_STR.format(",".join(book_ids))

        print(query)

        filtered_book_ids = get_book_ids(query)
        if not book_ids:
            book_ids = filtered_book_ids
        else:
            book_ids = book_ids.intersection(filtered_book_ids)

        if not book_ids:
            break

    book_count = len(book_ids)
    filter_by_id = True
    if not filters or (filters and len(filters) == 1 and filters[0] == "page"):
        filter_by_id = False
        book_count = get_book_count()

    query_str = request.query_string.decode('utf-8')
    result = {
        "count": book_count,
        "next_page": get_next_page_link(book_count, page, query_str),
        "previous_page": get_prev_page_link(book_count, page, query_str),
        "results": get_books_detail(page=page, book_ids=book_ids, filter_by_id=filter_by_id)
    }
    return result


def get_book_count():
    data = DbService.execute_query(BOOK_COUNT)
    for row in data:
        return int(row[0])


def get_filter_key_value(filter_key, value):
    key = filter_key
    if filter_key == "languages":
        filter_value = []
        languages = value.split(",")
        for i in range(len(languages)):
            filter_value.append("'{}'".format(languages[i].lower()))
        return key, [",".join(filter_value)]

    if filter_key == "topic":
        filter_value = []
        topics = value.split(",")
        for i in range(len(topics)):
            filter_value.append("lower(name) like '%{}%'".format(topics[i].lower()))

        return key, [" or ".join(filter_value)]

    if filter_key == "search":
        data = value.strip().lower().split(" ")
        print(data)
        if len(data) == 1:
            key = "author"
        else:
            return key, data

    if filter_key in ["author", "title", "mime_type", "search"]:
        value = value.lower()

    return key, [value]


def get_book_ids(query):
    book_ids = set()
    data = DbService.execute_query(query)
    for row in data:
        book_ids.add(str(row[0]))

    return book_ids


def get_books_detail(page=1, book_ids=[], filter_by_id=True):
    books = []
    str_book_ids = ",".join(book_ids)
    max_books = page * 25
    skip_books = (page - 1) * 25

    query = BOOK_DETAILS_BY_ID.format(str_book_ids, max_books)
    if not filter_by_id:
        query = BOOK_DETAILS.format(max_books)
        print(query)

    count = 0
    data = DbService.execute_query(query)
    if not data:
        return

    for row in data:
        count += 1
        if count <= skip_books:
            continue

        book = {}
        book_id = row[0]
        book["id"] = book_id
        book["download_count"] = row[1]
        book["media_type"] = row[2]
        book["title"] = row[3]
        book["authors"] = get_book_authors(book_id)
        book["bookshelves"] = get_bookshelves(book_id)
        book["languages"] = get_book_languages(book_id)
        book["formats"] = get_book_formats(book_id)
        book["subjects"] = get_book_subject(book_id)
        books.append(book)

    return books


def get_next_page_link(book_count, current_page, query_str):
    total_pages = book_count / PAGE_SIZE
    if current_page < total_pages:
        filters = remove_page_filter(query_str)
        if current_page > 1 or not filters:
            next_page = "{}?{}page={}"
        else:
            next_page = "{}?{}&page={}"

        return next_page.format(BASE_URL, filters, current_page+1)

    return None


def get_prev_page_link(book_count, current_page, query_str):
    total_pages = book_count / PAGE_SIZE
    if current_page == 1 or total_pages < current_page:
        return None

    filters = remove_page_filter(query_str)
    prev_page = current_page - 1
    return "{}?{}page={}".format(BASE_URL, filters, prev_page)


def remove_page_filter(query_str):
    return query_str.split("page=")[0]


def get_book_authors(book_id):
    query = BOOK_AUTHORS.format(book_id)
    data = DbService.execute_query(query)
    author_details = []
    author_detail = {}
    for row in data:
        author_detail["name"] = row[0]
        author_detail["birth_year"] = row[1]
        author_detail["death_year"] = row[2]
        author_details.append(author_detail)

    return author_details


def get_bookshelves(book_id):
    query = BOOKSHELVES.format(book_id)
    data = DbService.execute_query(query)
    bookshelfs = []
    for row in data:
        bookshelfs.append(row[0])

    return bookshelfs


def get_book_languages(book_id):
    query = BOOK_LANGUAGES.format(book_id)
    data = DbService.execute_query(query)
    languages = []
    for row in data:
        languages.append(row[0])

    return languages


def get_book_formats(book_id):
    query = BOOK_FORMAT.format(book_id)
    book_formats = {}
    data = DbService.execute_query(query)
    for row in data:
        book_formats[row[0]] = row[1]

    return book_formats


def get_book_subject(book_id):
    query = BOOK_SUBJECTS.format(book_id)
    data = DbService.execute_query(query)
    subjects = []
    for row in data:
        subjects.append(row[0])

    return subjects



