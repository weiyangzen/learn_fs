# File Research: sources/os/bsd/freebsd-src/sys/kern/tty_inq.c

## Purpose
Implements the TTY input queue: block allocation, canonical line boundaries, quote bits, erase support, secure flushing, reprint iteration, and zero-copy-ish reads to userspace.

## Main Structures and State
- `struct ttyinq_block`: doubly-linked 128-byte data block plus per-byte quote bitmap.
- `ttyinq_zone`: UMA zone for input blocks.
- Queue offsets track begin, canonicalized line start, reprint position, end, block pointers, block count, and quota.
- `kern.tty_inq_flush_secure` controls whether flush zeroes buffered data.

## Core Behavior
- `ttyinq_setsize()` adjusts quota and allocates blocks, temporarily dropping the TTY lock.
- `ttyinq_free()` flushes and frees all blocks.
- `ttyinq_write()` appends bytes and sets/clears quote bits.
- `ttyinq_write_nofrag()` requires enough room for the whole write.
- `ttyinq_canonicalize()` marks all current input readable; `ttyinq_canonicalize_break()` scans backward for newline/EOF/EOL-style break characters.
- `ttyinq_findchar()` searches canonicalized bytes for a break character while honoring quote bits.
- `ttyinq_read_uio()` removes data and copies to userspace, using a fast path that temporarily removes whole blocks before `uiomove()`.
- `ttyinq_peekchar()` and `ttyinq_unputchar()` support erase/backspace behavior at the queue tail.
- Reprint-position helpers and line iterators support canonical retyping and display-width recalculation.

## Dependencies
Used heavily by `tty_ttydisc.c`; relies on TTY lock discipline and UMA.

## Notes and Risks
- Quote bits are essential for distinguishing literal control characters from active line-editing delimiters.
- Secure flush is password-conscious and zeroes all block data by default.
- Callers must respect assumptions around `flen` trimming and block-crossing reads.
