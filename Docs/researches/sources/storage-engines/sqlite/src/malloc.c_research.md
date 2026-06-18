# sources/storage-engines/sqlite/src/malloc.c

## Purpose

`malloc.c` is SQLite's high-level memory allocation wrapper. It sits above the selected low-level allocator in `sqlite3GlobalConfig.m` and implements public allocation APIs, memory usage accounting, soft and hard heap limits, memory pressure handling, per-connection lookaside-aware allocation helpers, string duplication helpers, and connection-level OOM state propagation. The low-level allocator files (`mem0.c`, `mem1.c`, `mem2.c`, `mem3.c`, `mem5.c`, or platform-specific alternatives) provide `sqlite3_mem_methods`; this file enforces SQLite API semantics and integrates allocation with status counters and database-handle error state.

## Important APIs, Types, And Functions

Public APIs implemented here include `sqlite3_release_memory`, `sqlite3_soft_heap_limit64`, `sqlite3_soft_heap_limit`, `sqlite3_hard_heap_limit64`, `sqlite3_memory_used`, `sqlite3_memory_highwater`, `sqlite3_malloc`, `sqlite3_malloc64`, `sqlite3_msize`, `sqlite3_free`, `sqlite3_realloc`, and `sqlite3_realloc64`. Internal allocation APIs include `sqlite3MallocInit`, `sqlite3MallocEnd`, `sqlite3MallocMutex`, `sqlite3HeapNearlyFull`, `sqlite3Malloc`, `sqlite3MallocSize`, `sqlite3DbMallocSize`, `sqlite3DbFreeNN`, `sqlite3DbNNFreeNN`, `sqlite3DbFree`, `sqlite3Realloc`, `sqlite3MallocZero`, `sqlite3DbMallocZero`, `sqlite3DbMallocRaw`, `sqlite3DbMallocRawNN`, `sqlite3DbRealloc`, `sqlite3DbReallocOrFree`, `sqlite3DbStrDup`, `sqlite3DbStrNDup`, `sqlite3DbSpanDup`, `sqlite3SetString`, `sqlite3OomFault`, `sqlite3OomClear`, and `sqlite3ApiExit`.

The central local state is `Mem0Global mem0`, which stores the static memory mutex, soft limit (`alarmThreshold`), hard limit (`hardLimit`), and atomic `nearlyFull` signal. The functions also interact heavily with `sqlite3GlobalConfig.m`, `sqlite3GlobalConfig.bMemstat`, global status counters such as `SQLITE_STATUS_MEMORY_USED`, and per-connection fields including `db->mallocFailed`, `db->lookaside`, `db->pnBytesFreed`, `db->nVdbeExec`, `db->u1.isInterrupted`, and parse error state.

## Control Flow

Initialization starts in `sqlite3MallocInit()`: if no low-level allocator has been configured, it calls `sqlite3MemSetDefault()`, obtains the static memory mutex, normalizes page-cache buffer configuration, and calls the low-level allocator's `xInit`. Shutdown calls `xShutdown` and clears `mem0`.

`sqlite3Malloc()` filters zero and oversized requests, then either enters `mem0.mutex` and calls `mallocWithAlarm()` with accounting enabled or calls `xMalloc` directly when memstatus is disabled. `mallocWithAlarm()` rounds through `xRoundup`, updates highwater request size, checks the soft threshold, releases cache memory if needed, enforces the hard heap limit, calls `xMalloc`, and updates memory-used and allocation-count status counters. Reallocation follows the same pattern in `sqlite3Realloc()`: NULL and zero sizes are normalized to malloc/free behavior, size is rounded, the hard limit is checked against growth, `xRealloc` is invoked, and memory-used counters are adjusted by the size delta.

Per-connection allocation flows through `sqlite3DbMallocRawNN()`. If lookaside is enabled and the request fits, it pops from the small or full-size lookaside freelists or initial slot lists. Otherwise it calls `dbMallocRawFinish()`, which uses heap allocation and marks `sqlite3OomFault(db)` on failure. Freeing through `sqlite3DbFreeNN()` pushes lookaside blocks back to the correct freelist, optionally accumulates size into `db->pnBytesFreed`, or marks the allocation as heap and calls `sqlite3_free()`. Reallocation preserves lookaside pointers when the new size still fits; otherwise it copies out of lookaside into a new block or delegates heap reallocation.

OOM handling is connection-sticky. `sqlite3OomFault()` sets `db->mallocFailed`, interrupts active VDBEs, disables lookaside, and records parse errors. Later allocations on the same connection fail consistently until `sqlite3OomClear()` runs when no VDBEs are executing. `sqlite3ApiExit()` maps pending OOM or `SQLITE_IOERR_NOMEM` into `SQLITE_NOMEM_BKPT` and updates the connection error.

## State And Persistence Behavior

This file has no on-disk persistence, but it strongly affects persistent database operations by deciding whether page-cache memory can be released and whether VDBEs must be interrupted. The global soft heap limit triggers `sqlite3_release_memory()`, which delegates to pcache memory release when `SQLITE_ENABLE_MEMORY_MANAGEMENT` is enabled. The hard heap limit prevents growth before calling the low-level allocator. Status counters persist for the lifetime of the process or until reset through status APIs. Per-connection OOM state persists across calls until the API boundary clears it, deliberately making allocation failure ordering predictable within one database handle.

Lookaside slots are transient connection-local memory pools. Their freelists are not persisted, but their state must remain consistent across parser, VDBE, schema, and extension allocations. `db->pnBytesFreed` supports measurement-only passes where freeing records sizes rather than releasing memory.

## Dependencies And Integration Points

`malloc.c` depends on `sqliteInt.h`, low-level `sqlite3_mem_methods`, mutexes, atomic helpers, status counters, pcache memory release, debug memory typing (`sqlite3Memdebug*`), lookaside macros and types, VDBE interruption state, parser error reporting, and public initialization. It is invoked by nearly every SQLite subsystem, including btree, pager, parser, VDBE, schema, extension loading, URI parsing, and string formatting.

## Risks And Edge Cases

Risks concentrate around accounting correctness and OOM semantics. If a low-level allocator's `xSize` or `xRoundup` is inconsistent, global memory counters and hard-limit decisions become wrong. The hard-limit checks use current memory status before allocation/reallocation; stale status counters can reject or allow allocations incorrectly. Realloc failure must leave the original allocation valid. Lookaside pointer range checks must distinguish small slots, full slots, and heap blocks exactly, especially with two-size lookaside enabled. `sqlite3OomFault()` must avoid marking benign malloc failures as fatal. `sqlite3ApiExit()` requires the connection mutex; calling it outside that contract is unsafe. Oversized `u64` requests must be blocked before conversion to signed `int`.

## Test Signals

Useful tests include public malloc/realloc/free semantics for zero, NULL, oversized, and same-size requests; status counter and highwater updates; soft heap limit release behavior; hard heap limit rejection; OOM fault injection with sticky `db->mallocFailed`; parser/VDBE interruption on OOM; lookaside allocation, fallback, free, resize, and reconfigure-busy behavior; `sqlite3DbReallocOrFree()` ownership transfer on failure; `sqlite3_msize()` accuracy; benign malloc sections; and debug memory type assertions for heap versus lookaside allocations.
