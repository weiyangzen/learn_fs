# File Research: sources/teaching/xv6-riscv/kernel/elf.h

Defines the ELF executable metadata consumed by `exec.c`.

Contents:
- `ELF_MAGIC` identifies valid ELF binaries.
- `struct elfhdr` defines the ELF file header, including entry point and program header table location.
- `struct proghdr` defines loadable segment metadata.
- `ELF_PROG_LOAD` and segment permission flags map ELF program headers to user PTE permissions.

Filesystem relevance: executable loading reads ELF headers and segments from inodes using `readi()`, making this header part of the filesystem-to-process image path.
