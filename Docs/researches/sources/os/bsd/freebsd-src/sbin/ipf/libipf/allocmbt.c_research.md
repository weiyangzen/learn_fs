# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/allocmbt.c

This file allocates and initializes an `mb_t` packet buffer wrapper.

`allocmbt()` allocates the structure, sets `mb_len`, clears `mb_next`, and points `mb_data` at the embedded `mb_buf`.

The `len` value is recorded but no bounds check is performed against the embedded buffer size here.
