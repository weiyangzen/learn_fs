# File Research: sources/os/plan9/9front/sys/src/cmd/7c/swt.c

Mixed backend support file for switch lowering, bitfields, constant multiplication emission, global data emission, object serialization, history records, and ABI alignment.

Key functions:
- `swit1`/`swit2` generate switch dispatch as linear compares, binary decision trees, or direct jump tables via `OCASE`/`ABCASE`.
- `bitload` extracts bitfields with masking and sign/zero-extending shifts.
- `bitstore` masks, shifts, merges, and stores bitfield values back into containing storage.
- `outstring` buffers string data into fixed `NSNAME` chunks emitted as `ADATA`.
- `mulcon` consumes recipes from `mulcon0` and emits shift/add/sub instruction sequences for multiplication by constants.
- `gextern` emits global data initialization, with special handling for vlong constants and endianness.
- `outcode`, `zwrite`, `zname`, and `zaddr` serialize compiler `Prog` records and symbol table references to the object stream.
- `outhist` emits source history/path records.
- `align` and `maxround` implement target struct/argument/automatic storage alignment.

Important details:
- Object symbol references use a small `NSYM` rolling cache.
- `zaddr` upgrades too-large `D_CONST` offsets to `D_DCONST`.
- Alignment treats parameters and aggregates according to this backend’s 64-bit ABI expectations, while preserving Plan 9 compiler conventions.

Filesystem relevance: indirect compiler/object emission support.
