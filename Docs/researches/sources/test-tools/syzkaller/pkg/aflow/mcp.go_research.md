# sources/test-tools/syzkaller/pkg/aflow/mcp.go

Purpose: exports aflow tools and actions as Model Context Protocol tools for `tools/syz-mcp`, and provides an MCP-ready `Context`.

Important APIs/types/functions: `MCPTools` maps `*mcp.Tool` to `MCPToolFunc`. `NewMCPContext` initializes `Context` with absolute workdir, cache, supplied state, no-op trajectory events, and real time. `registerMCPTool` wraps `funcTool` with input/output schemas and structured results. `registerMCPAction` wraps `funcAction` as an MCP tool with empty input schema and output extracted from context state. `registerMCP` normalizes names by replacing dashes with underscores, de-duplicates names, and skips disabled registration or `llmSetResultsTool`.

Control flow: registrations create `mcp.Tool` descriptors from aflow schema helpers, then install handler closures into the global map. Tool handlers convert bad-call errors into MCP error results while propagating infrastructure errors. Action handlers execute the action and convert context state to declared result shape.

State and persistence: global process state includes `MCPTools`, `registerMCPTools`, and `mcpToolNames`. Per-call state lives in `Context.state`; no on-disk persistence is introduced.

Dependencies and integration: depends on `modelcontextprotocol/go-sdk/mcp`, syzkaller `osutil`, `trajectory`, and schema conversion helpers. The `init` function registers `session-initializer`, which seeds `ReproSyz`, `ReproOpts`, and `ReproC` for MCP workflows.

Risks and test signals: risks are global registration order, name collisions after dash-to-underscore normalization, schema panics from missing tags, and inconsistent error mapping. Coverage is indirect through schema/tool tests and MCP consumers rather than explicit tests in this file.
