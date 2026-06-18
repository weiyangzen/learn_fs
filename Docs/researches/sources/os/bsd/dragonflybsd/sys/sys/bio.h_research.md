# File Research: sources/os/bsd/dragonflybsd/sys/sys/bio.h

Read completely: 105 lines.

This header defines DragonFlyBSD's BIO request object for block/storage I/O.

Key contents:
- Forward declarations for BIO tracking and disk structures.
- `biodone_t` completion callback typedef.
- `struct bio` with driver queue links, BIO stack pointers, buffer back-pointer, completion callback, logical offset, driver-private pointer, CRC, flags, and caller-info unions.
- BIO flags for synchronous completion, waiters, and done state.
- Prototype for `bio_start_transaction()`.

Important interactions:
- Used by buffer cache and device strategy paths; `buf.h` embeds arrays of BIOs in each buffer.
- Caller-owned and driver-owned info fields are explicitly separated.

Security/reliability notes:
- The BIO stack is a core storage-layer contract. Strategy layers must use the BIO passed to them rather than assuming `bio_buf->b_vp` matches their target.
