# File Research: sources/teaching/minix/minix/fs/mfs/utility.c

`utility.c` contains byte-order conversion helpers for MFS on-disk structures. `conv2` returns a 16-bit value unchanged when `norm` is true, otherwise swaps its two bytes. `conv4` returns a 32-bit value unchanged when native, otherwise swaps the low and high 16-bit halves through `conv2` and recombines them in reversed order.

These helpers are used for superblock fields, inode fields, bitmap chunks, directory inode numbers, and indirect zone entries. Current `read_super` sets `native = 1` for accepted V3 filesystems, but the conversion layer remains part of the shared MFS logic.
