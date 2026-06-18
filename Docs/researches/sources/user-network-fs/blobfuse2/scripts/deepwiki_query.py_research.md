<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/deepwiki_query.py -->
# sources/user-network-fs/blobfuse2/scripts/deepwiki_query.py

## Purpose
Command-line MCP client that asks DeepWiki a repository question and prints the answer.

## Important APIs, Types, and Functions
`MCPClient` manages streamable HTTP transport and an MCP `ClientSession`. `connect_to_server` initializes the session. `ask_deepwiki` calls tool `ask_question` with `repoName` and `question`. `cleanup` exits async contexts. `main(repo, title, body)` connects, combines title/body, prints the response, and cleans up.

## Control Flow and State
The script loads `.env`, validates three CLI arguments, then runs the async main. Session and stream contexts are instance state and must be cleaned up in `finally`.

## Dependencies and Integration Points
Depends on `mcp`, `httpx`, `python-dotenv`, and network access to `https://mcp.deepwiki.com/mcp`. It is called by `call_agent.py`.

## Risks and Edge Cases
Imports include unused modules. `ask_deepwiki` returns `result.content`, which may be a list of MCP content objects rather than plain text; callers stringify stdout. There is no timeout in this script itself, relying on caller process timeout. Network/MCP failures propagate.

## Test Signals
A successful run prints DeepWiki content. Failures are surfaced by nonzero exit and stderr when invoked from `call_agent.py`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/deepwiki_query.py -->
