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
            fig = pio.from_json(response.content[0].text)
        return fig
    else:
        return df
