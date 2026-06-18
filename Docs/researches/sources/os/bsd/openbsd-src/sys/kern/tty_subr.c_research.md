# File Research: sources/os/bsd/openbsd-src/sys/kern/tty_subr.c

TTY clist helper implementation.

This file implements the classic terminal character-list abstraction as fixed-size ring buffers with optional quote-bit storage. `clalloc()` allocates the byte ring and, when requested, a compact bitset for `TTY_QUOTE`; `clfree()` zeroes and releases both buffers. All mutating queue operations mask TTY interrupts with `spltty()` rather than using mutexes, which matches the low-level terminal path this code serves.

The byte movement routines cover single-character and bulk queue operations. `getc()` removes from the front, restores `TTY_QUOTE` from the bitset, clears consumed storage, wraps `c_cf`, and nulls front/last pointers on empty. `putc()` inserts at `c_cl`, tracks quote bits, handles wraparound, and reports full queues with `-1`. `q_to_b()` copies out contiguous runs while clearing data and quote bits, while `b_to_q()` copies buffer data into free ring segments and returns the untransferred count. `ndflush()` drops bytes from the front, and `unputc()` removes from the tail.

The scanning helpers support line discipline consumers. `ndqb()` counts contiguous bytes until a character with selected flag bits or quote state is encountered. `firstc()` and `nextc()` iterate without interrupt masking, with an explicit caller contract that no `getc()` may invalidate the pointer sequence. `catq()` either swaps same-sized queues when the destination is empty or falls back to repeated `getc()`/`putc()`.

Notable constraints: quote support is optional and callers that pass `TTY_QUOTE`-sensitive flags must ensure `c_cq` exists; `catq()` silently stops appending if `to` fills because `putc()` return values are ignored; and the ring pointer invariants depend on interrupt exclusion rather than general-purpose locking.
