# File Research: sources/virtualization/nbdkit/server/debug-flags.c

Purpose: Parses and applies `-D NAME.FLAG=N` debug flags for the server, plugins, and filters.

Core behavior:
- Stores flags in a linked list of `struct debug_flag`.
- `add_debug_flag` validates the required `NAME.FLAG=N` shape.
- `nbdkit_parse_int` parses the assigned integer value.
- `symbol_of_debug_flag` synthesizes a global variable name as `NAME_debug_FLAG`, replacing dots with underscores.

Application:
- `apply_debug_flags(dl, name)` scans pending flags matching the backend/server name.
- It resolves each synthesized symbol with `dlsym`.
- When present, it writes the requested integer value into that symbol.
- Missing symbols produce warnings, but the flag is still marked used for that name.

Cleanup:
- `free_debug_flags` emits warnings for flags never applied to any backend/server.
- It frees name, flag, symbol, and list nodes.

Dependencies:
- Uses `dlfcn.h`, `strndup`, and parsing helpers from the public nbdkit API.
- The global `debug_flags` head is declared in `main.c`/`internal.h`.
