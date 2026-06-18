# File Research: sources/local-fs/ocfs2-tools/libo2cb/o2cb_crc32.c

## Purpose

Implements CRC32 hashing for libo2cb.

## Main Contents

- Contains a 256-entry CRC32 table copied from Linux kernel/modutils genksyms code.
- `partial_crc32_one()` updates CRC for one byte.
- `partial_crc32()` processes a NUL-terminated string.
- `crc32()` wraps with initial/final XOR.
- Public `o2cb_crc32()` returns the CRC32 of a string.

## Dependencies and Integration

- Includes `o2cb_crc32.h`.
- Used by `o2cb_abi.c` to derive SysV semaphore keys from heartbeat region names.

## Research Notes

- Operates on C strings, not arbitrary buffers; embedded NUL bytes terminate hashing.
