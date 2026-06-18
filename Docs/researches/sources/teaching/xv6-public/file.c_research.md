# File Research: sources/teaching/xv6-public/file.c

Implements kernel file descriptor object management.

Key behavior:
- Maintains global `ftable` of `NFILE` `struct file` entries under a spinlock.
- `filealloc`, `filedup`, and `fileclose` manage file object references.
- `fileclose` dispatches final close to `pipeclose` or `iput` inside a transaction.
- `filestat` reports inode metadata.
- `fileread` routes reads to pipe or inode and advances file offset.
- `filewrite` routes writes to pipe or inode and splits large inode writes into log-sized transactions.

Important interactions:
- Offsets live in shared `struct file`, so duplicated/forked descriptors share offset state.
- Write chunking is necessary because the log has a small fixed transaction size.
