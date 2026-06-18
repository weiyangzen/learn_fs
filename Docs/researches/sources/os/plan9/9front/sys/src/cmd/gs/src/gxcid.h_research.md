# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcid.h

Common CID/CMap metadata definitions.

Key definitions:
- Defines `gs_cid_system_info_t` with `Registry`, `Ordering`, and `Supplement`.
- Provides structure descriptor macros for a single CIDSystemInfo value and arrays of CIDSystemInfo values, with two const-string pointer fields.
- Declares `cid_system_info_set_null` and `cid_system_info_is_null`.

Behavior contract:
- A null CMap CIDSystemInfo is represented by empty `Registry` and `Ordering` strings plus `Supplement == 0`.

Dependencies:
- Includes `gsstype.h` for Ghostscript string and structure-descriptor support.

Research notes:
- This header is small but important for CID-keyed font identity; it gives shared representation to CMap and CID font code.
