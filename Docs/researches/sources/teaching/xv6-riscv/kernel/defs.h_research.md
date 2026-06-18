# File Research: sources/teaching/xv6-riscv/kernel/defs.h

Central declaration header for kernel-internal functions and forward declarations. It groups prototypes by implementation file.

Major API groups:
- Buffer cache: `binit`, `bread`, `bwrite`, `brelse`, pin/unpin.
- Filesystem: inode allocation, locking, path lookup, read/write, stat, truncation, orphan reclaim.
- File table: allocation, dup, close, read/write/stat dispatch.
- Log: `begin_op`, `end_op`, `log_write`.
- Process, VM, traps, locks, UART, PLIC, virtio disk, and syscall helpers.

Filesystem relevance: this file captures the cross-module contract among `bio.c`, `fs.c`, `log.c`, `file.c`, `sysfile.c`, `proc.c`, and `vm.c`. It also shows the teaching kernel’s intentionally flat internal API surface.
