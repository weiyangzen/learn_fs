# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/alist_new.c

This file creates one parsed address-list node from a host/address string.

`alist_new()` chooses IPv4 or IPv6 when family is unspecified, handles leading whitespace and `!` negation, parses optional CIDR prefix, computes default classful IPv4 masks for abbreviated IPv4 forms, builds IPv6 masks with `fill6bits()`, resolves the host with `gethost()`, and stores family, address, mask, and negation in `alist_t`.

Implementation notes and risks:
- The input string is mutated temporarily when splitting on `/`.
- IPv4 abbreviated address handling preserves classful mask behavior.
- Invalid family, prefix, or hostname resolution returns `NULL`.
