# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getifname.c

This helper converts a kernel `ifnet` pointer to an interface name string.

For Solaris it reads a `qif_t` via `kmemcpy()` and duplicates `qf_name`. For other platforms it reads `struct ifnet` and duplicates `if_xname`.

Special pointer values map to display markers: `(void *)-1` returns `!`, `NULL` returns `-`, and failed kernel copy returns `X`.

Returned normal interface names are heap-allocated and must be freed by callers.
