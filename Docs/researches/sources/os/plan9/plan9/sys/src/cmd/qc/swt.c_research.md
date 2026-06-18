# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/swt.c

Mixed backend support for switches, bitfields, static data, object serialization, and ABI layout.

Key responsibilities:
- Lowers switch statements using linear compare chains for small cases and binary search for larger case lists.
- Generates bitfield load/store sequences with shifts and masks.
- Buffers string literals into `ADATA` chunks.
- Emits multiply-by-constant code using sequences from `mul.c`.
- Emits global/static data, including special handling for 64-bit constants and endianness.
- Serializes `Prog` objects to the Plan 9 object stream with symbol-cache records, addresses, history records, signatures, and constants.
- Computes structure, argument, and automatic-variable alignment, including double-containing aggregate rules.
- Computes rounded frame/argument sizes.

Dependencies:
- Tightly coupled to `txt.c`, `mul.c`, `q.out.h`, Plan 9 object format, and generic compiler history/symbol/type systems.

Notable risks:
- Object encoding uses compact symbol slots and binary address records; compatibility depends on exact field layout.
- Alignment logic encodes PowerPC ABI and big-endian assumptions.
