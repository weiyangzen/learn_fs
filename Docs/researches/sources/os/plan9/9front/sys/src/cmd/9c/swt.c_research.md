# File Research: sources/os/plan9/9front/sys/src/cmd/9c/swt.c

This file contains backend support routines for the Plan 9 C compiler targeting Power64. It handles switch-code lowering, bitfield load/store generation, static data emission, constant-multiply strength reduction, object-file symbol/address serialization, source-history emission, and target-specific alignment.

Key routines:
- `swit1` and `swit2` generate switch dispatch code. Small switch sets become linear equality tests; larger sets become binary-search compare/branch trees.
- `bitload` and `bitstore` extract and update C bitfields using shifts, masks, and temporary registers.
- `outstring`, `sextern`, and `gextern` emit string/static initializer data through `ADATA` pseudo-instructions.
- `mulcon` uses `Multab` recipes from `mulcon0` to replace multiplication by constants with shifts/adds/subtracts where possible.
- `outcode`, `zwrite`, `zname`, and `zaddr` serialize compiler `Prog` instructions into the Plan 9 object format consumed by `9l`.
- `outhist` emits `AHISTORY` records for source path/line tracking, including Windows path normalization.
- `align` and `maxround` define target ABI alignment for structs, arguments, automatics, and big-endian parameter adjustment.

Important interactions:
- Depends heavily on global codegen state from `gc.h`: `firstp`, `lastp`, `p`, `pc`, `types`, `debug`, `symstring`, and string buffers.
- Emits object records compatible with `9l/obj.c` decoding.
- Uses Power64-specific object address classes such as `D_CONST`, `D_DCONST`, `D_SCONST`, `D_BRANCH`, and `D_EXTERN`.

Research notes:
- Switch lowering explicitly works around immediates outside signed 16-bit range by subtracting into a temporary before compare.
- 64-bit constants are split in `gextern` according to target endian behavior detected through `align(..., Aarg1)`.
- This file is part of the compiler-to-linker contract: mistakes here affect linker parsing and final relocation.
