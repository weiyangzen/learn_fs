# File Research: sources/os/plan9/9front/sys/src/cmd/aux/flashfs/flashfs.h

Role: Central flashfs declarations, constants, structures, globals, and function prototypes.

Key constants:
- Sector magic `ROO0`, compact journal transaction type bytes, size limits (`MAXFSIZE`, `MAXNSIZE`), encoded record size estimates, hash table size, special time value, and max write chunk size.

Core types:
- `Extent` maps file byte ranges to sector addresses.
- `Exts` stores head/tail extent list.
- `Entry` represents files/directories and overlays directory-specific and file-specific state in a union.
- `Dirr` tracks directory read cursors.
- `Jrec` is the in-memory journal record.
- `Renum` records old/new sector numbers for extent renumbering.

Exposed APIs:
- Data backend, compact integer encoding, journal conversion/formatting, filesystem load and journal write functions, entry tree operations, and 9P serving.

Globals:
- Sector geometry, sector buffer, root entry, readonly state, clock delta, active generation parity, magic bytes, used space, journal limit, and max write size.
