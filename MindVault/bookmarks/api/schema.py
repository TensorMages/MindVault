import strawberry
from typing import List, Optional
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()

@strawberry.type
class Bookmark:
    url: str
    name: str
    dateAdded: str

@strawberry.type
class User:
    email: str
    name: str
    bookmarks: List[Bookmark]

def getAllUsers():
    records, summary, keys = driver.execute_query(
        '''
        MATCH (u:User)-[:LIKES]->(b:Bookmark) 
        RETURN u.name AS name, u.email AS email, COLLECT(PROPERTIES(b)) AS bookmarks
        ''',
        database_="neo4j",
    )

    users = []
    for record in records:
        user_data = record.data()
        bookmarks = []
        for bookmark_data in user_data["bookmarks"]:
            bookmarks.append(Bookmark(
                url=bookmark_data["url"],
                name=bookmark_data["name"],
                folder=bookmark_data["folder"],
                dateAdded=bookmark_data["dateAdded"],
            ))
        users.append(User(
            email=user_data["email"],
            name=user_data["name"],
            bookmarks=bookmarks
        ))

    return users

def getUser(email: str):
    records, summary, keys = driver.execute_query(
        '''
        MATCH (u:User)-[:LIKES]->(b:Bookmark) 
        WHERE u.email=$email 
        RETURN u.name AS name, u.email AS email, COLLECT(PROPERTIES(b)) AS bookmarks
        ''',
        email=email,
        database_="neo4j",
    )

    if len(records) == 0:
        return None
    
    user_data = records[0].data()
    
    bookmarks = []
    for bookmark in user_data["bookmarks"]:
        bookmarks.append(getBookmark(bookmark["url"]))

    return User(
        email=user_data["email"],
        name=user_data["name"],
        bookmarks=bookmarks,
    )

def getAllBookmarks():
    records, summary, keys = driver.execute_query(
        '''
        MATCH (b:Bookmark) 
        RETURN PROPERTIES(b) AS bookmarks
        ''',
        database_="neo4j",
    )

    bookmarks = []
    for record in records:
        bookmark_data = record.data()["bookmarks"]
        bookmarks.append(getBookmark(bookmark_data["url"]))

    return bookmarks

def getBookmark(url):
    records, summary, keys = driver.execute_query(
        "MATCH (b:Bookmark) WHERE b.url=$url RETURN PROPERTIES(b) AS properties",
        url=url,
        database_="neo4j",
    )

    if len(records) == 0:
        return None
    
    bookmark_data = records[0].data()["properties"]
    
    return Bookmark(
        url=bookmark_data["url"],
        name=bookmark_data["name"],
        dateAdded=bookmark_data["dateAdded"],
    )

# Queries
@strawberry.type
class Query:
    @strawberry.field
    def bookmark(self, url: str) -> Optional[Bookmark]:
        return getBookmark(url)
    
    @strawberry.field
    def user(self, email: str) -> Optional[User]:
        return getUser(email)
    
    @strawberry.field
    def users() -> List[User]:
        return getAllUsers()
    
    @strawberry.field
    def bookmarks() -> List[Bookmark]:
        return getAllBookmarks()

schema = strawberry.Schema(query=Query)