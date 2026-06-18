# sources/test-tools/syzkaller/syz-agent/agent/mcp.go

Purpose: exposes syzkaller aflow MCP tools over streamable HTTP.

Important APIs/types/functions: `mcpHandler` and `toolHandler`.

Control flow: `mcpHandler` creates an MCP server, registers every `aflow.MCPTools` entry, and returns a streamable HTTP handler with JSON responses and one-hour sessions. Each tool handler unmarshals arguments, serializes requests per session with a mutex, lazily creates an `aflow.Context`, closes it when the session ends, and dispatches the tool function.

State and persistence: session map stores per-session context objects; aflow cache persists according to the cache passed in from `agent.go`.

Dependencies and integration points: integrates `github.com/modelcontextprotocol/go-sdk/mcp` with syzkaller `pkg/aflow`.

Risks: session contexts use `context.Background`, so request cancellation does not stop long operations. Session cleanup depends on `req.Session.Wait`.

Test signals: no direct unit tests here.
