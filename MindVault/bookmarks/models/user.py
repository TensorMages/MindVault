from pydantic import BaseModel, Field
from loguru import logger

class UserModel(BaseModel):
    """
    A model representing a user.
    """
    name: str = Field(..., description="The name of the user")
    email: str = Field(..., description="The email ID of the user")
    
    def __str__(self):
        return f"{self.name} ({self.url}) added on {self.dateAdded}"
    
    def create_node(self, driver):
        summary = driver.execute_query(
            '''
            MERGE (u:User { email: $email, name: $name })
            ''',
            email=self.email,
            name=self.name,
            database_="neo4j",
        ).summary
        
        if(summary.counters.nodes_created == 0):
            logger.info("User already exists.")
        else:
            logger.info("Created {nodes_created} User node in {time} ms.".format(
                nodes_created=summary.counters.nodes_created,
                time=summary.result_available_after
            ))
            
    __repr__ = __str__
