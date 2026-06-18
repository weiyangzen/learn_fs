# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_main.c

## Purpose
`mdcache_main.c` wires MDCACHE into the FSAL module system. It defines module identity and fsinfo defaults, global cache statistics and entry pool, export create/update/uninit paths, package init/unload, and optional DBus reporting.

## Important APIs, Types, and Functions
- Global `MDCACHE` defines the module and default FSAL capability information.
- `mdcache_fsal_init()` registers the FSAL, sets module ops, and initializes object-handle ops.
- `mdcache_pkginit()` creates the entry pool, initializes LRU, and initializes the cache inode hash package.
- `mdcache_fsal_create_export()` allocates an MDCACHE export wrapper, initializes export ops and upcall ops, creates the underlying FSAL export, stacks MDCACHE above it, starts dirmap LRU if supported, updates `op_ctx`, and marks upcalls ready.
- `mdcache_export_uninit()` unwinds export setup on startup error.
- `mdcache_fsal_update_export()` forwards export updates to the lower FSAL.
- `mdcache_fsal_unload()` destroys hash/LRU/pool state and unregisters the module.
- `mdcache_dbus_show()` and `mdcache_utilization()` report stats and LRU/FD utilization when DBus is enabled.

## Control Flow
Initialization registers the FSAL first, then package initialization creates runtime cache resources. Export creation happens after the lower FSAL is known. MDCACHE allocates a wrapper export, installs MDCACHE export/upcall operations, asks the lower FSAL to create its export with MDCACHE upcalls, takes references, stacks exports, initializes per-export dirmap support, and switches `op_ctx` to the MDCACHE export.

Unload reverses global state: hash package destruction, LRU shutdown, pool destruction, and FSAL unregister. Export update is intentionally thin because MDCACHE has no per-export config in this file.

## State and Persistence Behavior
This file owns global in-memory state: `mdcache_entry_pool`, `cache_st`, and the module descriptor. Export wrappers allocate transient names, entry lists, locks, dirmap state, and upcall readiness. No persistent data is stored; all state is recreated on server start.

## Dependencies and Integration Points
It integrates with FSAL registration, export stacking, lower-FSAL module ops, MDCACHE handle/export/upcall initialization, `mdcache_lru`, `mdcache_hash`, pool allocation, DBus, and global FD LRU counters. It also exposes delegation transition forwarding to the lower FSAL.

## Risks and Edge Cases
Potential issues include incomplete cleanup when export creation fails after lower-FSAL creation or dirmap init, reference mismatches between MDCACHE and lower FSAL modules, upcalls arriving before `up_ready_set()`, and shutdown ordering if LRU cleanup still references hash/export state. The dirmap failure path frees the wrapper but must also consider lower-FSAL export resources already created.

## Test Signals
Test startup/shutdown loops, export create failure injection at lower-FSAL create and dirmap init, export update pass-through, DBus counter reporting under cache activity, module unload after active/recent cache entries, and delegation transition forwarding.
