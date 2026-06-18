# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_config.h.in

## Summary
Autoheader template for generated `rumpuser_config.h`.

## Key Details
- Contains `#undef` entries for all Autoconf-detected headers, functions, types, libraries, and package metadata.
- Covers rumpuser portability features such as clocks, dynamic linker support, filesystem sync, aligned allocation, environment helpers, vector I/O, pthread naming signatures, and NetBSD-style device headers.
- Includes large-file knobs `_FILE_OFFSET_BITS` and `_LARGE_FILES`.
- Defines `_DARWIN_USE_64_BIT_INODE` to `1` unless already defined.

## Notes
This file is data for `config.status`; consumers use the generated header or the NetBSD defaults embedded in `rumpuser_port.h`.
