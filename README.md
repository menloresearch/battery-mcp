# Battery MCP Server

A Model Context Protocol server that provides battery materials validation capabilities. This server enables LLMs to verify invented bettery materials are novel and valid or not.

<img src="./assets/image.png" alt="Image" width="50%">

> [!CAUTION]
> This server can access local/internal IP addresses and may represent a security risk. Exercise caution when using this MCP server to ensure this does not expose any sensitive data.


## Available Tools

### `search_material`
Searches and returns relevant battery materials from the database.

**Parameters:**
- `formula` (string, required): Formula query for battery materials (e.g., "LiCoO2")
- `n` (integer, optional): Number of results to return (default: 5, min: 1, max: 100)

---

### `verify_input_material`
Validates whether a material exists in the database.

**Parameters:**
- `original_material` (string, required): Material formula to validate (e.g., "LiFePO4")

---

### `battery_material_validation`
Parses and validates battery materials from a query, comparing them against a reference material.

**Parameters:**
- `original_material` (string, required): Reference battery material (e.g., "LiCoO2")
- `query` (string, required): Comma-separated list of proposed materials (e.g., "Li2B4O7, Li1.06Ti2O4")


## Installation

This MCP server requires API key from [materials project](https://next-gen.materialsproject.org/), you can get api key and use it with env variable `MP_API_KEY`

```
export MP_API_KEY=
```

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will
use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *[battery-mcp](https://github.com/nguyenhoangthuan99/battery-mcp.git)*.

### Using PIP

Alternatively you can install `battery-mcp` via pip:

```
pip install battery-mcp
```

After installation, you can run it as a script using:

```
python -m battery_mcp
```

### Running with streamable-http

You can also deploy mcp as http server with streamable-http transport protocol

```
python -m battery_mcp --transport http --http-host 0.0.0.0 --http-port 8080
```

or using `uvx`
```
uvx battery-mcp --transport http --http-host 0.0.0.0 --http-port 8080
```
## Configuration

### Configure for Claude.app

Add to your Claude settings:

<details>
<summary>Using uvx</summary>

```json
{
  "mcpServers": {
    "fetch": {
      "command": "uvx",
      "args": ["battery-mcp"]
    }
  }
}
```
</details>

<details>
<summary>Using pip installation</summary>

```json
{
  "mcpServers": {
    "fetch": {
      "command": "python",
      "args": ["-m", "battery-mcp"]
    }
  }
}
```
</details>


## License

battery-mcp is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
