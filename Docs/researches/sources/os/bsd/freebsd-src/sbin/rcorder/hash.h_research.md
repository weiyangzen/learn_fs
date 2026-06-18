# File Research: sources/os/bsd/freebsd-src/sbin/rcorder/hash.h

Public interface and types for rcorder’s hash table.

Key elements:
- Defines `Hash_Entry`, `Hash_Table`, and `Hash_Search`.
- Provides `Hash_GetValue`, `Hash_SetValue`, and, under `ORDER`, `Hash_GetKey`.
- Declares initialization, deletion, lookup, creation, entry deletion, and enumeration functions.
- `Hash_Size` converts byte counts to word counts.

Dependencies:
- Requires `ClientData` and `Boolean` from `sprite.h`.

Research notes:
- This is generic infrastructure but tightly used by `rcorder.c` to map provision names to provider lists.
