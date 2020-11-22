BOOK_FILTER_STR = """
and book_id in ({})
"""

BOOK_COUNT = """
select count(*)
from books_book
"""

BOOK_DETAILS = """
SELECT
    gutenberg_id,
    COALESCE(download_count,0) as count, 
    media_type, 
    title 
FROM books_book 
ORDER BY count DESC 
LIMIT {}
"""

BOOK_DETAILS_BY_ID = """
SELECT 
    gutenberg_id, 
    COALESCE(download_count,0) as count,
    media_type, 
    title 
FROM books_book 
WHERE gutenberg_id in ({}) 
ORDER BY count DESC 
LIMIT {}
"""

BOOK_IDS_BY_LANGUAGE = """
select book_id
from books_book_languages bbl 
join books_language bl 
on bbl.language_id = bl.id
where code in ({})
"""

BOOK_IDS_BY_MIME_TYPE = """
select book_id 
from books_format bf 
where mime_type like '%{}%'
"""

BOOK_IDS_BY_AUTHOR = """
select book_id
from books_book_authors bba 
join books_author ba
on bba.author_id = ba.id 
where LOWER(ba.name) like '%{}%'
"""

BOOK_IDS_BY_TITLE = """
select gutenberg_id
from books_book bba  
where LOWER(bba.title) like '%{}%'
"""

BOOK_IDS_BY_TOPIC = """
select 	book_id
from books_book_subjects bbs 
join books_subject bs 
on bbs.subject_id = bs.id 
where {0}
UNION
select book_id
from books_book_bookshelves bbb 
join books_bookshelf bs 
on bbb.bookshelf_id = bs.id 
where {0}
"""

BOOK_ID_BY_AUTHOR_AND_TITLE = """
select bb.gutenberg_id 
from books_book_authors bba 
join books_author ba
on bba.author_id = ba.id
join books_book bb
on bba.book_id = bb.gutenberg_id 
where LOWER(ba.name) like '%{}%'
and lower(bb.title) like '%{}%'
"""

BOOK_AUTHORS = """
select 
    ba.name, 
    ba.birth_year, 
    ba.death_year
from books_book_authors bba 
join books_author ba 
on bba.author_id = ba.id 
where bba.book_id = {}
"""

BOOKSHELVES = """
select name
from books_book_bookshelves bbb 
join books_bookshelf bb
on bbb.bookshelf_id = bb.id 
where bbb.book_id = {}
"""

BOOK_LANGUAGES = """
select code
from books_book_languages bbl 
join books_language bl
on bbl.language_id = bl.id 
where bbl.book_id = {}
"""

BOOK_FORMAT = """
select mime_type, url 
from books_format bf 
where bf.book_id = {}
"""

BOOK_SUBJECTS = """
select name
from books_book_subjects bbs 
join books_subject bs
on bbs.subject_id = bs.id 
where bbs.book_id = {}
"""