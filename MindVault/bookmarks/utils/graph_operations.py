from loguru import logger

def clear_graph(driver):
    summary = driver.execute_query(
        "MATCH (n) DETACH DELETE n",
        database_="neo4j",
    ).summary
    logger.info("Graph cleared.")
