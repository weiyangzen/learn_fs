# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iplugin.h

Public/private plugin manager interface for interpreter plugins.

Key behavior:
- Forwards `i_ctx_t` and `gs_memory_t`.
- Defines plugin descriptor, instance, linked-list holder, and client-memory callback structs.
- A descriptor contains `type`, `subtype`, and an instance finalizer/deallocator.
- An instance embeds a descriptor pointer as base-class RTTI.
- `plugin_instantiation_proc` macro defines plugin factory signatures.
- `extern_i_plugin_table()` declares the external plugin factory table.
- Declares plugin memory setup, initialization, finalization, lookup, and list access functions.

Research notes:
- This is a small object-model layer for optional interpreter plugins such as font APIs.
- The client memory interface requires copying/allocation behavior supplied by the plugin manager.
