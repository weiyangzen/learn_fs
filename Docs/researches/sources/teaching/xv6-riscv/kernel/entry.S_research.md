# File Research: sources/teaching/xv6-riscv/kernel/entry.S

Boot entry assembly loaded by QEMU at `0x80000000`.

Important behavior:
- Defines `_entry` in `.text`.
- Computes an initial stack pointer from `stack0 + (hartid + 1) * 4096`.
- Reads `mhartid` to select a per-CPU boot stack.
- Calls `start()` in `start.c`.
- Spins forever if `start()` returns.

Filesystem relevance: indirect. It is part of the boot chain that eventually initializes memory, traps, buffer cache, inode table, file table, virtio disk, and the first process.
