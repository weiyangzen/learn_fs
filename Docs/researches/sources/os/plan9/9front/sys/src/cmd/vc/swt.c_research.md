# File Research: sources/os/plan9/9front/sys/src/cmd/vc/swt.c

Purpose: Switch lowering, bitfield helpers, string/static data emission, object output encoding, and alignment for the MIPS backend.

Key behavior:
- `swit1`/`swit2` lower switches as linear comparisons for small case counts and recursive binary-search comparisons for larger sets.
- `bitload` and `bitstore` load, mask, shift, merge, and store C bitfields.
- `outstring`, `sextern`, and `gextern` emit string and global/static data as `ADATA`.
- `mulcon` consumes constant multiply sequences from `mul.c` and emits shift/add/sub instructions.
- `outcode` writes history records, symbol table name records, and encoded `Prog` instructions.
- `zname`, `zaddr`, and `zwrite` implement the compact object-file instruction encoding.
- `outhist` emits source file history records, with Windows path handling.
- `align` and `maxround` define MIPS ABI alignment for structs, arguments, and autos.

Dependencies:
- Uses `gc.h`, `v.out.h` address classes/opcodes, `Biobuf`, `ieeedtod`, and generic compiler type/symbol/history state.

Notable details:
- Argument alignment applies a big-endian adjustment for narrow parameters when `thechar == 'v'`.
