# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/swt.c

Purpose: switch emission, bitfield operations, string/data output, constant-multiply use, object serialization, and layout/alignment helpers.

Key behavior:
- `swit1`/`swit2` emit switch comparisons; small switches are linear and larger ones use recursive binary splitting.
- `bitload` and `bitstore` extract/insert bitfields with shifts and masks.
- `outstring` accumulates string data into `ADATA` chunks of `NSNAME`.
- `mulcon` turns multiplication by selected constants into shift/add/sub sequences from `mul.c`.
- `gextern` emits initialized global data, with special handling for 64-bit constants.
- `outcode`, `zwrite`, `zname`, and `zaddr` serialize the backend instruction stream into Plan 9 object format.
- `outhist` emits source history, with Windows path handling.
- `align` and `maxround` implement MIPS ABI layout rules for structs, parameters, and autos.

Integration points:
- `txt.c` emits `Prog` records consumed by `outcode`.
- `cgen.c` calls bitfield and multiply helpers.
- Object format enums and address types come from `v.out.h`.

Risks:
- Symbol cache size `NSYM` affects object output symbol interning.
- Alignment behavior is ABI-defining and uses endian-specific parameter adjustment for `thechar == 'v'`.
- `mulcon` assumes integer constant conversion through `convvtox` preserves value before optimizing.
