# Gutendex Book API

## Overview
The API should support the following:
1.  Retrieval of books meeting zero or more filter criteria. Each query should return the following:
    - The number of books meeting the criteria
    - A list of book objects, each of which contains the following:
        - Title of the book
        - Information about the author
        - Genre
        - Language
        - Subject(s)
        - Bookshelf(s)
        - A list of links to download the book in the available format (mime-types)

2. The following rules apply:
    - In case the number of books that meet the criteria exceeds 25, the API should return only 25 books at a time and support the means of retrieving the next sets of 25 books till all books are retrieved.
    - The books should be returned in decreasing order of popularity, as measured by the number of downloads.
    - Data should be returned in a JSON format.
    - The following filter criteria should be supported:
    - Book ID numbers specified as Project Gutenberg ID numbers.
    - Language
    - Mime-type
    - Topic. Topic should filter on either ‘subject’ or ‘bookshelf’ or both. Case insensitive partial matches should be supported. e.g. ‘topic=child’ should among others, return books from the bookshelf ‘Children’s literature’ and from the subject _Child education_.
    - Author. Case insensitive partial matches should be supported.
    - Title. Case insensitive partial matches should be supported.

__Multiple filter criteria should be permitted in each API call and multiple filter values should be allowed for each criterion. e.g. an API call should be able to filter on `language=en,fr` and `topic=child, infant`.__

## Endpoint
I hosted the API on EC2 instance as a Flask application. The endpoint can be accessed at:

__`http://13.233.59.155:5000/get_books`__

## Request
Please make sure that you use exact same variable names in the request, of course with no particular order.

- __titles__
- __authors__
- __languages__
- __mime_types__
- __book_ids__
- __topics__
- __page__

## Response
```
{
 "count": <The number of books meeting the criteria>,
 "page": <Current page number>,
 "total_page": <Total number of pages in the query>,
 "books": <A list of books with decreasing order of popularity (number of downlaods)>
 }
```

**Note:** The extra two variables `page` and `total_page` had to add for pagination purpose, so that one can send request accordingly.

## Example

1. Multiple topics to search in Subjects and Bookshelves with partial search functionality.

    __`curl -X POST http://13.233.59.155:5000/get_books -d 'topics=india, child, woman'`__
    
    ![](https://i.imgur.com/Zcx0IvN.png)
    
    ![](https://i.imgur.com/zdXi82G.png)
    
    Please note that we got __4625__ books with that criteria and there are total __185 pages__, each having __25 books__.
    
    If we want to go to the page number 2, simply can simply specify the page number in the query.
    
    __`curl -X POST http://13.233.59.155:5000/get_books -d 'topics=india, child, woman&page= 2'`__
    
    And here we go:
    
    ![](https://i.imgur.com/g7zUKM2.png)
    
2. Multiple filters with different criteria

    __`curl -X POST http://13.233.59.155:5000/get_books -d 'topics=india, child, woman&languages=la'`__
    
    ![](https://i.imgur.com/C5j6uxX.png)
    
3. With more filters

    __`curl -X POST http://13.233.59.155:5000/get_books -d 'topics=india, child, woman&languages=en&mime_types=text/html'`__

    ![](https://i.imgur.com/s2t3ic2.png)
