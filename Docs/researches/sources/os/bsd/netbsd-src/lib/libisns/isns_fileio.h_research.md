# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_fileio.h

Private header for `libisns` vector I/O wrappers.

Includes errno/types/uio headers and declares:
- `isns_file_writev`
- `isns_file_readv`

Used by internal socket/file transport code through `isns_config.h`.
