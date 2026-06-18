# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/count4bits.c

This helper validates and counts contiguous one bits in an IPv4 netmask.

`count4bits()` converts the mask from network byte order, counts leading one bits, reconstructs the expected contiguous mask, and returns the prefix length only if the original mask matches. Non-contiguous masks return `-1`.
