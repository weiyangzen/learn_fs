# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iplugin.h

Public/internal plugin manager interface for Ghostscript interpreter plugins.

Key contents:
- Forward-declares `i_ctx_t` and `gs_memory_t` if not already defined.
- Declares plugin holder, instance, descriptor, and client-memory structures.
- Defines `i_plugin_descriptor` with `type`, `subtype`, and `finit` destructor.
- Defines `i_plugin_instance` as a base object containing a descriptor pointer.
- Defines `i_plugin_holder` as a linked-list node.
- Defines `i_plugin_client_memory`, a callback-based allocation interface.
- Defines `plugin_instantiation_proc` and `extern_i_plugin_table` macros.
- Declares memory wrapper, init/finalize, lookup, and list-access functions.

Notable dependencies:
- Paired with `iplugin.c`.
- Used by interpreter features such as FAPI bridges.

Research notes:
- The plugin interface is intentionally small: type/subtype RTTI, destructor, and custom allocation callbacks.
- The instantiation table is provided externally by generated configuration.
