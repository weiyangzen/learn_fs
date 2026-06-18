# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc/net/Makefile.inc

## Summary
SPARC network byte-order build fragment.

## Key Details
- Adds assembly sources `htonl.S`, `htons.S`, `ntohl.S`, and `ntohs.S`.

## Notes
SPARC uses architecture-specific assembly for host/network conversion routines.
