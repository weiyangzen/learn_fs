# File Research: sources/teaching/xv6-public/log.c

Implements xv6’s simple physical redo log for filesystem updates.

Key behavior:
- `initlog` reads superblock log location and recovers any committed transaction.
- On-disk log format is header block containing home block numbers followed by logged block copies.
- `begin_op` reserves log capacity or sleeps while committing/near capacity.
- `end_op` decrements outstanding operation count and commits when the last filesystem operation exits.
- `write_log`, `write_head`, and `install_trans` implement commit: copy cache blocks to log, commit header, install home blocks, clear header.
- `log_write` records a modified buffer, absorbs duplicate block writes, and pins it by setting `B_DIRTY`.

Important interactions:
- Filesystem syscalls must bracket mutating operations with `begin_op`/`end_op`.
- The design commits only when no FS syscalls are outstanding, simplifying transaction isolation.
