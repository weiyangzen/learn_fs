# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/trace.h

Declares the ftrace event surface for XFS online scrub and repair. The file explicitly states these tracepoints are not a stable kernel ABI.

Trace coverage:
- Scrub lifecycle events: start, done, deadlock retry, repair attempt/done, dirtree start/done.
- Filesystem gate events for enabling/disabling live-update hooks.
- Vectored scrub events for vector-head input, per-vector item/outcome, and barrier failures.
- Error and marking events for filesystem blocks, inode numbers, file blocks, operation errors, incomplete scans, btree operation errors, btree corruption, and cross-reference failures.
- Quota scrub events for dquot iteration and quotacheck errors.
- Inode allocation, filesystem counter calculation/range checks, fsfreeze/fsthaw, and refcount mismatch diagnostics.
- `xfile` and `xfarray` events covering create/destroy, load/store/seek/folio/discard, array creation, sort phases, sort scans, and sort stats.
- Realtime summary record-free tracing when realtime support is enabled.
- Inode scan events covering cursor movement, visited/skipped inodes, batch iget, and retry waits.
- Nlink scrub events for dirent/parent-pointer/metafile collection, live updates, zero-link checks, incore updates, and inode comparison.
- Parent pointer, directory tree, directory path, path outcome, dirtree evaluation, live path changes, and metadata path lookup events.
- Repair events for extent reaping, reap limits, selected extents, rebuilt btree discoveries, bmap/rmap/refcount records, root finding, reservation calculations, counter resets, newbt allocation/free/claim, dinode fixes, inode fixes, CoW repair, quota repair, nlink repair, rmap live updates, tempfile creation/prealloc/copyin, fork reaping, xattr/parent-pointer salvage and replay, directory salvage/rebuild/replay/adoption, symlink salvage/rebuild/reset, unlinked-list repair, dirtree repair, metadata path repair, and realtime bitmap/rtrmap repair.

String tables and enums:
- Maps scrub types, scrub flags, scrub state flags, refcount domains, group types, rmap update operations, and directory path outcomes to readable trace output.
- Uses `TRACE_DEFINE_ENUM` for ftrace encoding of enum values.
- Ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE scrub/trace`, and `include <trace/define_trace.h>` for kernel trace generation.

Important implementation detail:
- Many events are factored through `DECLARE_EVENT_CLASS` plus `DEFINE_EVENT` wrappers to keep related tracepoint layouts consistent.
