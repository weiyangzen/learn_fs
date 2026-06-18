# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns.h

Public `libisns` API header.

Defines opaque `ISNS_HANDLE` and `ISNS_TRANS` types, invalid handle constants, TLV iteration constants, and public functions for:
- library init/stop
- adding server connections
- starting registration refresh
- creating/freeing/sending transactions
- adding and retrieving TLVs
- adding string TLVs

The API exposes protocol transactions while keeping implementation details private.
