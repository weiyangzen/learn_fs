# File Research: sources/os/linux/linux/fs/xfs/xfs_trace.h

## Purpose

`xfs_trace.h` defines the Linux ftrace/tracepoint instrumentation surface for XFS. It is not a stable ABI; it is a developer and diagnostic interface for observing allocation, logging, transaction, inode, directory, attribute, reflink, realtime, health, media verification, and shutdown behavior inside the kernel XFS implementation.

The file is intentionally broad: it centralizes `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, and `TRACE_DEFINE_ENUM` declarations so XFS subsystems can emit consistent structured events without each C file defining its own trace metadata.

## Main Contents

- Tracepoint include guard and `TRACE_SYSTEM xfs` setup, followed by forward declarations for XFS structs used by trace prototypes.
- Unit and naming conventions for trace fields, such as `agno`, `agino`, `agbno`, `rgbno`, `startblock`, `fileoff`, `daddr`, `bbcount`, `rtx`, `rtxcount`, `owner`, `pos`, and `bytecount`.
- Event classes and generated events for:
  - Attribute list iteration, attribute operations, delayed attribute state machines, and parent-pointer listing.
  - Allocation group and generic group reference tracking, including active/passive refs.
  - Realtime groups, zoned realtime allocation, open-zone accounting, and zone garbage collection when `CONFIG_XFS_RT` is enabled.
  - Inode garbage collection, block garbage collection, shrinker scans, inode cache walks, and speculative preallocation cleanup.
  - Buffer cache lifecycle, buffer IO errors, buffer log items, and transaction buffer joins/logging.
  - Inode locks, inode references, inode lifecycle, file operations, iomap mappings, writeback invalidation, and direct/buffered/DAX IO.
  - Directory, namespace, rename, dir2, xattr, and da-btree operations.
  - Quota objects, quota transaction deltas, and dquot reservation accounting.
  - Log grants, log tickets, CIL/AIL log item movement, iclog state transitions, log recovery records/items, log forcing, and shutdown.
  - Free-space allocation, AGF state, busy extents, discard, btree cursor operations, and fake-root btree rebuild state.
  - Deferred operation framework events and deferred extent-free, bmap, rmap, refcount, and exchange-mapping intents.
  - Reverse mapping, refcount btree, reflink, copy-on-write, unshare, and swapext/remap paths.
  - `fsmap`/`getfsmap` key and mapping iteration.
  - Transaction reservation calculation and transaction lifecycle events.
  - Unlinked inode bucket updates and unlinked-list reloads.
  - Health state transitions, health monitor ring-buffer operations, health event formatting, media/file IO error reporting, and media verification.
  - Optional in-memory buffer and in-memory btree events under `CONFIG_XFS_MEMORY_BUFS` and `CONFIG_XFS_BTREE_IN_MEM`.

## Important Design Points

- Most event families are implemented as event classes plus small `DEFINE_*_EVENT` macros. This keeps repeated tracepoint payloads consistent across many XFS operations.
- The tracepoints record stable diagnostic identifiers instead of raw internal pointers where possible: filesystem device, group type/index, inode number, fork, owner, file offset, physical block, extent length, reservation state, flags, and LSN fields.
- Many enums are wrapped in `TRACE_DEFINE_ENUM` so ftrace can decode symbolic names from ring-buffer values.
- Several trace classes are group-type aware. Newer XFS code can report both allocation groups and realtime groups through `enum xfs_group_type` and `XG_TYPE_STRINGS`.
- Log and transaction tracepoints align with `xfs_trans.c`, `xfs_log.c`, CIL, and AIL behavior: transaction allocation/commit/roll/free, reservation calculations, log grant waits, ticket regrant/ungrant, iclog state changes, and recovery replay.
- Health monitor tracepoints expose both internal queue behavior and formatted events for mount, filesystem, group, inode, media, file-range, shutdown, and lost-event domains.
- The file ends with `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `<trace/define_trace.h>` inclusion, making this the header that instantiates tracepoint definitions when included from the corresponding trace compilation unit.

## Cross-File Relationships

- Transaction tracepoints are emitted from `xfs_trans.c` for allocation, duplicate, roll, commit, cancel, free, item add/free, and transaction reservation calculation.
- Buffer-related tracepoints are emitted by XFS buffer cache and buffer-log-item code.
- Log grant, iclog, AIL, and log recovery tracepoints are used by log manager, CIL, AIL, and recovery code.
- Rmap, refcount, bmap, extent-free, and exchange-map deferred-intent tracepoints mirror deferred operation item types implemented across XFS intent item files.
- Reflink and COW tracepoints are used by XFS reflink, iomap, and writeback paths.
- Health monitor and media verification tracepoints connect to XFS health reporting, forced shutdown, media-scrub, and file IO error reporting code.

## Risks / Review Notes

- This file is a diagnostic contract, not a user ABI, but tracepoint field names and formatting are still heavily relied on by debugging tools and developer workflows.
- Because many event classes dereference internal objects in `TP_fast_assign`, call sites must only trace while the referenced mount, inode, group, buffer, dquot, or cursor remains valid.
- Changes to enum values or flag sets should update both `TRACE_DEFINE_ENUM` declarations and `__print_symbolic` / `__print_flags` string tables, or trace output becomes harder to decode.
- Adding support for new XFS group/device domains must preserve formatting consistency for `agno`/`rgno`, `agbno`/`rgbno`, and generic `gbno` fields.
- The file is compiled through the kernel tracepoint machinery; syntax errors in one trace event can break XFS builds even if the tracepoint is rarely enabled.
