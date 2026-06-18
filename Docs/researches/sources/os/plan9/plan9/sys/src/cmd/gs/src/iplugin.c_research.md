# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iplugin.c

Ghostscript interpreter plugin manager implementation.

Key behavior:
- Defines client-memory allocation/free wrappers backed by raw non-GC memory.
- `i_plugin_make_memory` initializes an `i_plugin_client_memory` wrapper around `gs_memory_t`.
- `i_plugin_init` walks `i_plugin_table`, instantiates each plugin, allocates a holder in raw memory, and links it into `i_ctx_p->plugin_list`.
- `i_plugin_finit` walks the plugin list, calls each instance descriptor’s finalizer, and frees holders.
- `i_plugin_get_list` returns the context’s plugin list.
- `i_plugin_find` searches by descriptor `type` and `subtype`.

Notable dependencies:
- Uses `icstate.h` for context plugin-list storage.
- Uses `iplugin.h` for plugin descriptors and table declarations.

Research notes:
- The file explicitly uses raw memory so plugin instances survive PostScript VM restore operations long enough to finalize objects they manage.
- If an instantiation succeeds but later holder allocation fails, the new instance is not finalized before returning fatal.
