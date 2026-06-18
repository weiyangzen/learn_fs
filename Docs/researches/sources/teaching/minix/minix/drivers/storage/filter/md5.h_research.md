# File Research: sources/teaching/minix/minix/drivers/storage/filter/md5.h

## Purpose
Declares MD5 types and functions for the filter checksum layer.

## Contents
- Defines `uint32` as `unsigned long`, requiring at least 32 bits.
- Defines `struct MD5Context` with four digest words, two bit-count words, and a 64-byte input buffer.
- Declares `MD5Init`, `MD5Update`, `MD5Final`, and `MD5Transform`.

## Integration Notes
Included by `sum.c` and implemented by `md5.c`.

## Risks
The typedef is intentionally portable but may be wider than 32 bits; implementation masks arithmetic to preserve MD5 behavior.
