# File Research: sources/virtualization/libguestfs/daemon/htonl.c

Compatibility implementations for byte-order conversion functions.

Important behavior:
- Provides `htonl`/`ntohl` when `HAVE_NTOHL` is absent.
- Provides `htons`/`ntohs` when `HAVE_NTOHS` is absent.
- Uses compile-time endian macros and `bswap_32`/`bswap_16`.
- Avoids Windows headers due to conflicting declarations.

Filesystem relevance: protocol portability support, especially for XDR/network-order daemon communication.
