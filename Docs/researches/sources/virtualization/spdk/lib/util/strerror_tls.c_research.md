# File Research: sources/virtualization/spdk/lib/util/strerror_tls.c

This file provides `spdk_strerror()`, a thread-local strerror wrapper.

It declares a `static __thread char strerror_message[64]`, calls `spdk_strerror_r()` into that buffer, and returns the thread-local pointer. The result is overwritten by the next `spdk_strerror()` call on the same thread.

This is a convenience layer over `string.c`’s portable `spdk_strerror_r()` implementation.
