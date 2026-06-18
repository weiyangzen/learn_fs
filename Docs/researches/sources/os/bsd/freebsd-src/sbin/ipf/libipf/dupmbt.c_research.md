# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/dupmbt.c

This helper duplicates one `mb_t` packet buffer wrapper.

`dupmbt()` allocates a new `mb_t`, copies length, clears `mb_next`, preserves the same relative `mb_data` offset into the embedded buffer, and copies the active data bytes.

It duplicates only one node, not an `mb_t` chain.
