# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/Makefile

## Summary
Installs public CD9660/ISO filesystem headers.

## Main Responsibilities
- Sets `INCSDIR=/usr/include/isofs/cd9660`.
- Installs cd9660 headers including extern, mount, node, Rock Ridge, and ISO format headers.
- Includes `bsd.kinc.mk`.

## Integration Notes
These headers define the ABI and kernel interfaces for ISO 9660 filesystem support.
