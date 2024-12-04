from datetime import date
from loguru import logger
import os

from pydantic import BaseModel, Field

class BookmarkModel(BaseModel):
    """
    A model representing a bookmark.
    """

    name: str = Field(..., description="The name of the bookmark")
    url: str = Field(..., description="The URL of the bookmark")
    folder: str = Field(..., description="The folder of the bookmark")
    dateAdded: date = Field(..., description="The date the bookmark was added")

    def __str__(self):
        return f"{self.name} ({self.url}) added on {self.dateAdded}"
    
    def to_dict(self):
        # Converts the model to a dictionary with JSON-compatible data
        data = self.dict()
        data['dateAdded'] = self.dateAdded.isoformat()  # Convert date to string
        return data
    
    def create_node(self, driver):
        summary = driver.execute_query(
            '''
            MATCH (u:User) WHERE u.email = $userEmail
            MERGE (b:Bookmark { url: $url })
            ON CREATE SET b.name = $name, b.dateAdded = $dateAdded
            WITH u, b
            MERGE(u)-[:LIKES { folder: $folder }]->(b)
            ''',
            userEmail=os.getenv("USER_EMAIL"),
            url=self.url,
            name=self.name,
            folder=self.folder,
            dateAdded=self.dateAdded,
            database_="neo4j",
        ).summary
        
        if summary.counters.nodes_created == 0:
            logger.info("Bookmark already exists.")
        else:
            logger.info("Created {nodes_created} Bookmark node in {time} ms.".format(
                nodes_created=summary.counters.nodes_created,
                time=summary.result_available_after
            ))

    __repr__ = __str__