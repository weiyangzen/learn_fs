# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/net/Makefile.inc

## Summary
SPARC64 network byte-order build fragment.

## Key Details
- Adds `htonl.S`, `htons.S`, `ntohl.S`, and `ntohs.S`.

## Notes
Uses architecture-specific assembly implementations for byte-order functions.
