# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/count6bits.c

This helper counts one bits in an IPv6 mask represented as four 32-bit words.

It walks from index 3 down to 0, adding 32 for all-ones words and then counting leading ones in the first non-all-ones word. It does not reconstruct and validate contiguity the way `count4bits()` does.
