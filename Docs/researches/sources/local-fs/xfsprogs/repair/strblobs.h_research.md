# File Research: sources/local-fs/xfsprogs/repair/strblobs.h

Header for deduplicated string blob storage.

Exports opaque `struct strblobs` and functions to:
- Initialize/destroy a string blob table.
- Store a string and receive an `xfblob_cookie`.
- Load a string by cookie.
- Lookup an existing string by bytes, length, and directory hash.

The interface is designed around explicit string lengths and xfs directory hash values.
