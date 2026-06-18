# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/string/Makefile.inc

This make include selects or1k string/memory implementations. In debug builds it maps object targets to generic C sources for easier debugging; otherwise it builds assembly versions of `memcmp.S`, `bcopy.S`, and `memmove.S`.

The conditional source mapping affects performance and debuggability. It must keep object names aligned with libc’s expected string routine symbols.
