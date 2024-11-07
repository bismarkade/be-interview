# Notes

End points-->
path validation

```python
 from fastapi import Path

 @app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail='Item not found')
```

Query validation

```python
 from fastapi import Query

@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def read_books_by_publish_date(
    published_date: int = Query(gt=1999, lt=2031)
    ):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return
```
