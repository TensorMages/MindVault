from loguru import logger
from pathlib import Path
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

from browser.chromium import get_bookmarks_from_browser
from models.user import UserModel
from utils.graph_operations import clear_graph

load_dotenv()

URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

def main():
    # Initiate Neo4j driver
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        
    # Configure logger
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    logger.add(log_dir / "bookmarks.log", rotation="10 MB", level="INFO")
    
    # Truncate the graph database (For local database ONLY)
    # clear_graph(driver)
    
    # Get local user details and create node
    user = UserModel(
        name=os.getenv("USER_NAME"),
        email=os.getenv("USER_EMAIL")
    )
    user.create_node(driver)
    
    # Fetch and store all Chrome bookmarks for the local user
    # ??? Pass the user model as an argument ???
    bookmarks = get_bookmarks_from_browser(driver, os.getenv("USER_EMAIL"), "chrome")
    
    print(bookmarks[:10])
        
main()