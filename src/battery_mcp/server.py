from typing import Annotated, Tuple
from urllib.parse import urlparse, urlunparse

import markdownify
import readabilipy.simple_json
from mcp.shared.exceptions import McpError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    ErrorData,
    TextContent,
    Tool,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)
from pydantic import BaseModel, Field, AnyUrl
from battery_mcp.tools import verify_input_material, battery_material_validation, search_material
from queue import Queue
import threading
import asyncio


class SearchMaterialInput(BaseModel):
    """Parameters for searching battery materials."""
    formula: Annotated[
        str,
        Field(description="formula query for battery materials e.g 'LiCoO2'")
    ]
    n: Annotated[
        int,
        Field(
            default=5,
            description="Number of results to return",
            gt=0,
            le=100
        )
    ]


class VerifyInputMaterialInput(BaseModel):
    """Parameters for validating if a material exists in database."""
    original_material: Annotated[
        str,
        Field(description="Material formula to validate")
    ]


class BatteryMaterialValidationInput(BaseModel):
    """Parameters for validating and comparing battery materials."""
    original_material: Annotated[
        str,
        Field(
            description="Original battery material from user's input to be used as reference",
            min_length=1,
            examples=["LiCoO2", "LiFePO4"]
        )
    ]
    query: Annotated[
        str,
        Field(
            description="Proposed materials separated by commas, e.g. 'Li2B4O7, Li1.06Ti2O4' - will be automatically split and stripped",
            min_length=1,
            examples=["Li2B4O7, Li1.06Ti2O4"]
        )
    ]


async def serve(
) -> None:
    """Run the Battery MCP server.
    """
    server = Server("battery-mcp")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="search_material",
                description="""Search and return relevent materials from DB.""",
                inputSchema=SearchMaterialInput.model_json_schema(),
            ),
            Tool(
                name="verify_input_material",
                description="""Tool to check if the input material from user is valid or not.""",
                inputSchema=VerifyInputMaterialInput.model_json_schema(),
            ),
            Tool(
                name="battery_material_validation",
                description="""Tool to parse battery material from query then validate the material capacity using for battery. """,
                inputSchema=BatteryMaterialValidationInput.model_json_schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name, arguments: dict) -> list[TextContent]:
        try:
            if name == "search_material":
                func = search_material
                args = SearchMaterialInput(**arguments)
            elif name == "verify_input_material":
                func = verify_input_material
                args = VerifyInputMaterialInput(**arguments)
            elif name == "battery_material_validation":
                func = battery_material_validation
                args = BatteryMaterialValidationInput(**arguments)
            else:
                raise McpError(ErrorData(code=INVALID_PARAMS,
                               message=f"tool name '{name}' is not supported."))
        except ValueError as e:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))

        try:
            result_queue = Queue()

            def wrapped_func():
                result_queue.put(func(**args.dict()))
            thread = threading.Thread(target=wrapped_func)
            thread.start()

            while True:
                if not thread.is_alive():
                    break
                await asyncio.sleep(1.)
            response = result_queue.get()
        except Exception as e:
            raise McpError(ErrorData(code=INTERNAL_ERROR,
                           message=f"Failed to execute tool '{name}': {e}"))

        return [TextContent(type="text", text=response)]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
