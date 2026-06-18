# File Research: sources/teaching/xv6-riscv/kernel/main.c

Kernel supervisor-mode main entry after `start()`.

Important behavior:
- CPU 0 initializes console, printing, physical memory, kernel page table, process table, traps, PLIC, buffer cache, inode table, file table, virtio disk, and the first process.
- Other CPUs wait for `started`, then initialize paging, trap vector, and PLIC hart state.
- All CPUs enter `scheduler()`.

Filesystem relevance: establishes initialization order. Buffer cache, inode table, file table, and virtio disk are ready before the first process runs; filesystem superblock/log initialization is deferred until `forkret()` in process context.
