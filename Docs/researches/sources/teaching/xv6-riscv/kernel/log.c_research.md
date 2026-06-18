# File Research: sources/teaching/xv6-riscv/kernel/log.c

Implements xv6’s physical redo log for filesystem crash recovery.

Important behavior:
- `initlog()` initializes log metadata and replays any committed transaction.
- `recover_from_log()` reads the on-disk header, installs logged blocks, then clears the log.
- `begin_op()` reserves log space and sleeps if a commit is active or space may run out.
- `end_op()` decrements outstanding operations and commits when the last operation exits.
- `log_write()` records modified block numbers, absorbs duplicate writes, and pins buffers in cache.
- `commit()` writes dirty cache blocks to the log, commits by writing the header, installs home blocks, then clears the header.

Filesystem relevance: all mutating filesystem syscalls depend on this file. It provides transaction grouping, log absorption, buffer pinning, recovery, and bounds that shape `filewrite()` chunking.
