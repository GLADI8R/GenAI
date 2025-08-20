from fastmcp import Client
import pandas as pd
import plotly.io as pio

config = {
    "mcpServers": {
        "SQL": {"transport": "http", "url": "http://localhost:8001/mcp"},
        "Mongo": {"transport": "http", "url": "http://localhost:8002/mcp"},
        "Chart": {"transport": "http", "url": "http://localhost:8003/mcp"},
    }
}

client = Client(config)        

async def orchestrate(db_choice: str, query: str, intent: str):
    """
    Orchestrates the query execution based on the selected database and intent.

    Args:
        db_choice (str): The database choice ("SQL", "MongoDB", or "File Upload").
        query (str): The query to execute.
        intent (str): The intent of the query (e.g., "chart", "dataframe").
    
    Returns:
        pd.DataFrame or plotly.graph_objects.Figure: The result of the query execution.
        str: The generated Python code for chart creation if intent is "chart".
    """

    df, fig = None, None
    async with client:
        # tools = await client.list_tools()
        # print(tools)
        if db_choice == "SQL":
            response = await client.call_tool("SQL_run_sql", {"query": query})
            state = eval(response.content[0].text)
            df = pd.DataFrame(data=eval(state.get("result")), columns=state.get("columns"))
        elif db_choice == "MongoDB":
            response = await client.call_tool("Mongo_run_mongo", {"query": query})
            state = eval(response.content[0].text)
            df = pd.DataFrame(data=eval(state.get("result")))

    if intent == "chart":
        if df is None:
            raise ValueError("DataFrame is empty. Cannot create chart without data.")
    
        # Create chart using the ChartAgent
        if df.empty:
            raise ValueError("DataFrame is empty. Cannot create chart without data.")
        
        async with client:
            response = await client.call_tool("Chart_create_chart", {
                "user_prompt": query,
                "df": df.to_dict(orient="records")
            })
            evaulated_response = eval(response.content[0].text)
            fig = pio.from_json(evaulated_response[0])
            query_code = evaulated_response[1]
        return fig, query_code
    else:
        return df, None
