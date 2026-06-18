# File Research: sources/local-fs/jfsutils/libfs/logform.c

This file formats a JFS journal for mkfs or logredo recovery. Its single public function, `jfs_logform()`, creates or refreshes inline and external logs.

Behavior:
- Allocates and initializes a `struct logsuper` at log page 1.
- Determines log size from inline log extent parameters or from the external device size, capped at 128 MB.
- Generates a UUID for a new external log or verifies an existing external log UUID.
- Fills log superblock fields: magic, version, `LOGREDONE` state, flags, size, block size, log2 block size, end pointer, UUID, label, and empty active list.
- Writes two initial log pages, including a `LOG_SYNCPT` record, then writes remaining log pages four at a time.
- Initializes log page sequence numbers so `findEndOfLog()` sees a simulated wrap layout after formatting.
- Shows a spinner only when stdout is a terminal, then flushes the device.

Integration points:
- Uses `ujfs_get_dev_size()`, `ujfs_rw_diskblocks()`, `ujfs_flush_dev()`, endian swapping helpers, and UUID functions.
- The exported prototype is declared in `logform.h`.
- Called by mkfs paths and by `recoverExtendFS()` in `logredo.c`.

Risks and notes:
- The external-log UUID verification appears suspicious: after reading the existing log superblock, it prints “Invalid log device” when `uuid_compare(log_sup->uuid, uuid)` returns equality. The comment says it should verify a match, so this condition may be inverted.
- Several early error returns after `calloc()` do not free `log_sup`; this is minor for command-line utilities but visible.
- The assignments to log record type use endian conversion in an unusual direction for constants; on little-endian this is harmless, but big-endian behavior depends on macro definitions and later logpage swapping.
