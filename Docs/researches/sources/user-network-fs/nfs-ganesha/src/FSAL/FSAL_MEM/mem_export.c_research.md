# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_export.c

Purpose: Implements FSAL_MEM export lifecycle, dynamic filesystem info, wire-handle endian normalization, NFS state allocation, fd-to-handle lookup, export op registration, async behavior configuration, export creation, and export update.

Important APIs and types: Core methods are `mem_release_export()`, `mem_get_dynamic_info()`, `mem_wire_to_host()`, `mem_free_state()`, `mem_alloc_state()`, `get_fsal_obj_hdl()`, `mem_export_ops_init()`, `str_async_type()`, `mem_create_export()`, and `mem_update_export()`. Configured async modes are `MEM_INLINE`, `MEM_FIXED`, `MEM_RANDOM`, and `MEM_RANDOM_OR_INLINE`.

Control flow: Export creation allocates `mem_fsal_export`, initializes object list and export lock, initializes export ops, loads async config, attaches the export to the FSAL, saves `CTX_FULLPATH(op_ctx)`, sets `op_ctx->fsal_export`, and links the export into `MEM.mem_exports`. Release cleans the root subtree, finalizes and frees the root handle under export lock, detaches export, frees ops, removes from MEM export list, destroys the lock, and frees path/export. Update validates stacking via generic `update_export()`, parses new async config into a temporary struct, then atomically updates async delay/stall/type fields.

State and persistence: MEM FSAL state is entirely in memory. Exports own a root object tree, export path, object list, lock, and async behavior atomics. Dynamic filesystem info reports zeros for capacity and file counts. Per-NFS state owns an `fsal_fd`.

Dependencies and integration: Depends on MEM internals (`mem_int.h`, `mem_clean_export`, `mem_free_handle`, `mem_lookup_path`, `mem_create_handle`), Ganesha export manager/core, config parser, fd/state helpers, and optional LTTng tracepoints.

Risks: `mem_wire_to_host()` sets `fh_min = 1` but then reads a `uint64_t` hashkey and `ushort` length, so malformed short handles can be over-read. Dynamic info zeros may confuse clients expecting finite capacity. `get_fsal_obj_hdl()` assumes fd is the global `mh_file.fd` member, not a state fd. Release ordering must avoid races with concurrent operations during export teardown.

Test signals: Create/release export with populated tree, config parsing for all async modes and update_export changes, malformed wire handles shorter than hash+len, endian conversion, NFSv4 state allocation/free, async delay behavior in MEM I/O tests, and LTTng tracepoint compilation.
