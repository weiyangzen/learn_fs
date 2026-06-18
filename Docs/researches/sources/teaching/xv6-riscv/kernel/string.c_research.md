# File Research: sources/teaching/xv6-riscv/kernel/string.c

Provides minimal C string and memory routines for the kernel.

Functions:
- `memset`, `memcmp`, `memmove`, `memcpy`.
- `strncmp`, `strncpy`, `safestrcpy`, `strlen`.

Filesystem relevance: used heavily by filesystem code for inode/block structure copies, directory names, superblock reads, bitmap zeroing, and path/name handling.
