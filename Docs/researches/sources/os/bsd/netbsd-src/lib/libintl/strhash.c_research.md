# File Research: sources/os/bsd/netbsd-src/lib/libintl/strhash.c

Implements `__intl_string_hash`, the PJW-style hash used for gettext `.mo` hash-table lookup.

The function shifts the hash by four bits per byte, adds the byte, folds high bits, and returns a 32-bit hash. It is derived from NetBSD Citrus database hash code.
