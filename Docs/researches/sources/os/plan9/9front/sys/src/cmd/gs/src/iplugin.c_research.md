# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iplugin.c

Ghostscript interpreter plugin manager implementation.

Key behavior:
- Wraps raw, non-GC memory allocation in `i_plugin_client_memory`.
- `i_plugin_make_memory` installs allocation/free callbacks backed by a `gs_memory_t`.
- `i_plugin_init` iterates the generated `i_plugin_table`, instantiates each plugin, allocates an `i_plugin_holder`, and pushes it onto `i_ctx_p->plugin_list`.
- `i_plugin_finit` walks the plugin holder list, calls each plugin descriptor’s `finit`, and frees the holder.
- `i_plugin_get_list` returns the current context’s plugin list.
- `i_plugin_find` searches by descriptor `type` and `subtype`.

Notable dependencies:
- `malloc_.h`, `string_.h`, `ghost.h`, `gxalloc.h`, `ierrors.h`, `ialloc.h`, `iplugin.h`, and `icstate.h`.
- Generated or configured `i_plugin_table`.

Research notes:
- Plugin metadata lives in raw memory because it must survive PostScript VM restore operations and finalization of plugin-managed objects.
- If a plugin instantiation succeeds but later holder allocation fails, the function returns `e_Fatal` without visibly finalizing the just-created plugin instance.
- Plugin lookup is a simple linear search over the context list.
