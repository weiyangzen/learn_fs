# File Research: sources/local-fs/udftools/mkudffs/file.h

Header for mkudffs file/directory helpers.

Declares:
- Tag query helpers.
- File and directory creation APIs.
- Data, FID, and extended-attribute insertion APIs.
- Block allocation API.

Inline helpers:
- `clear_bits`: clears a run of bits in a space bitmap.
- `query_iuvdiu`: returns the implementation-use payload inside the first IUVD.
- `query_lvidiu`: returns the implementation-use payload inside the LVID after free-space and size tables.

Key role: exposes file-level UDF construction utilities to mkudffs generation code.
