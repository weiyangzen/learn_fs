# sources/storage-engines/wiredtiger/tools/wt-mcp/pyproject.toml

Purpose: defines the Python package metadata and dependencies for the WiredTiger MCP server.

Important APIs and control flow: `[project]` names the package `wt-mcp`, sets version `0.1.0`, requires Python `>=3.13`, and declares dependencies on `mcp[cli]>=1.23.0`, `pydantic>=2.11.4`, and `python-dotenv>=1.1.0`.

State and persistence behavior: static project metadata only.

Dependencies and integration points: consumed by Python packaging tools such as `uv`, `pip`, or build backends. It supports `server.py`, which imports FastMCP, Pydantic field helpers, and dotenv.

Risks: no build system table or script entry point is declared here, so invocation likely depends on direct script execution or surrounding tooling. Python 3.13 is a high floor and may limit developer environments.

Test signals: environment creation should install the three dependency families and allow `python server.py` to import MCP/Pydantic/dotenv before looking for WiredTiger build artifacts.
