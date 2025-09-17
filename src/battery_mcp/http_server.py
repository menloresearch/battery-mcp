from mcp.server.fastmcp import FastMCP
from battery_mcp.tools import verify_input_material as verify_input_material_func, battery_material_validation as battery_material_validation_func, search_material as search_material_func


def serve(host: str = "0.0.0.0", port: int = 22312):
    mcp = FastMCP("Battery-MCP", host=host, port=port)

    @mcp.tool()
    def search_material(formula: str, n: int) -> str:
        """
        Search and return relevent materials from DB.
        Args:
        - formula: formula query for battery materials e.g 'LiCoO2'
        - n: Number of results to return
        """
        return search_material_func(formula, n)

    @mcp.tool()
    def verify_input_material(original_material: str) -> str:
        """
        Tool to check if the input material from user is valid or not.
        Args:
        - original_material: Material formula to validate
        """
        return verify_input_material_func(original_material)

    @mcp.tool()
    def battery_material_validation(original_material: str, query: str) -> str:
        """
        Tool to parse battery material from query then validate the material capacity using for battery. 
        Args:
        - original_material: Original battery material from user's input to be used as reference
        - query: Proposed materials separated by commas, e.g. 'Li2B4O7, Li1.06Ti2O4' - will be automatically split and stripped
        """

        return battery_material_validation_func(original_material, query)

    mcp.run(transport='streamable-http')
