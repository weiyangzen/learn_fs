# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_trace.h

## Purpose
Defines the Linux tracepoint catalog for XFS. This header is not normal runtime logic; it declares `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TRACE_DEFINE_ENUM`, and trace formatting helpers that generate XFS ftrace/perf events when included through `<trace/define_trace.h>`.

The file explicitly states these tracepoints are not a stable kernel ABI. It also documents XFS trace formatting conventions for allocation groups, inodes, filesystem blocks, realtime blocks/extents, byte ranges, directory/xattr blocks, sizes, owners, and extent counts.

## Trace Surface
The file contains a large generated-style event surface:
- 93 event classes.
- 69 direct `TRACE_EVENT` declarations.
- 593 `DEFINE_*_EVENT` instantiations.
- 76 `TRACE_DEFINE_ENUM` declarations.

## Major Trace Families
- Attribute listing and attribute state-machine traces: attr list cursors, node descent, shortform/leaf/node attr operations, remote value operations, and deferred attr state returns.
- Mount, per-AG, generic group, realtime group, and zoned realtime traces: group references, zone state, zone allocation, zone GC, group intent drains, and realtime grow checks.
- Inode lifecycle and VFS operation traces: iget cache hits/misses, reclaim, inactive state, eof/cow block tags, locks, references, namespace operations, rename, file ioctl/fsync/readdir/getattr/setattr, page faults, timestamp ranges, and inode walks.
- Buffer and buffer-log-item traces: buffer allocation, holds, locks, IO, delwri queues, backing allocation mode, transaction buffer joins/releases, buffer item formatting/pin/unpin/commit/push paths, and buffer IO errors.
- Transaction and log traces: reservation calculations, transaction alloc/cancel/commit/dup/free/roll/add-item, log grant queues, ticket regrant/ungrant, CIL wait, log force, log item states, AIL push/insert/move/delete, tail assignment, iclog lifecycle, and log recovery records/items/buffer/inode/icreate replay.
- Allocation/free-space traces: AGF reads, extent busy tracking, allocation algorithms, exact/near/size allocation paths, AG reservations, metadata file reservations, free counter reservations, discard, and realtime discard/busy extents.
- Btree and metadata btree traces: cursor movement, update keys, allocation/free block, errors, fake roots, bulk-load geometry/blocks, in-memory btree buffer/free-space traces under config guards.
- Directory, dquot, and quota transaction traces: dir2 operations, dquot cache/reclaim/flush/read, transaction quota deltas, and detailed `xfs_dqtrx` reservation/delta state.
- Rmap/refcount/reflink traces: rmap map/unmap/convert/update/insert/delete/deferred intent traces, refcount lookup/extent mutations/adjustment/deferred operations, reflink remap/unshare/CoW/cancel/end-cow traces, and swapext rmap traces.
- Iomap and IO traces: buffered/direct/DAX read/write, iomap allocation/found/invalid, atomic-write CoW, delalloc ENOSPC, unwritten conversion, filesize updates, zero EOF, direct-write completion, splice read, zoned mapping, and writeback invalidation.
- Exchange-range, parent lookup, metadir, and health-monitor traces: exchange-range prep/flush/mappings/freshness/estimates/intents/extent-count deltas, getparents record emission, metadata directory updates, health monitor queue/copy/report/format/drop/merge, shutdown/media/file-IO error reporting, and media verification.

## Integration
This header is included by XFS implementation files to expose `trace_xfs_*` callsites. It depends on Linux tracepoint infrastructure and many XFS internal structures, but mostly uses forward declarations and field extraction inside `TP_fast_assign`.

The final include sequence sets:
- `TRACE_INCLUDE_PATH .`
- `TRACE_INCLUDE_FILE xfs_trace`
- `#include <trace/define_trace.h>`

This is the standard kernel tracepoint pattern that emits tracepoint definitions from the header.

## Conditional Coverage
Some trace families are compiled only when related features are enabled:
- `CONFIG_XFS_RT` for realtime, zones, realtime discard/busy allocation, and realtime grow geometry.
- `CONFIG_XFS_POSIX_ACL` and `CONFIG_COMPAT` for ACL and compat ioctl inode events.
- `CONFIG_XFS_DRAIN_INTENTS` for group intent drain events.
- `CONFIG_XFS_MEMORY_BUFS` for memory-backed buffer target events.
- `CONFIG_XFS_BTREE_IN_MEM` for in-memory btree events.

## Dependencies
Uses tracepoint macros, XFS format/type flag string tables from surrounding headers, core XFS structs such as mount, inode, buffer, transaction, log, btree cursor, dquot, rmap/refcount records, health monitor events, and Linux helpers for devices, inodes, iov iterators, block status, and folios.

## Risk Notes
- Trace format changes can break external tracing scripts despite the explicit non-ABI warning.
- Many `TP_fast_assign` blocks dereference internal structures; callsites must pass objects that are live and initialized for the fields being traced.
- Event formatting encodes subtle XFS concepts such as AG vs RTG group numbering, segmented fsblocks, legacy realtime behavior, lazy superblock counters, and CoW/refcount domains; incorrect trace use can mislead debugging even if it does not change filesystem behavior.
- Config-guarded events create feature-dependent tracing coverage, so diagnostics differ across kernel builds.
