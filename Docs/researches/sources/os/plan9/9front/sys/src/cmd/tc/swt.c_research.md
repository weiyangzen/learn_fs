# File Research: sources/os/plan9/9front/sys/src/cmd/tc/swt.c

Implements switch lowering, bitfield helpers, string/global data emission, object serialization, and target alignment.

Key points:
- `doswit` collects `case` nodes, validates defaults and duplicates, sorts cases, and dispatches to `swit1`.
- `swit1` emits either linear comparisons for small switches or recursive binary-search comparisons for larger switches.
- `bitload` and `bitstore` load, mask, sign/zero extend, merge, and store bitfield values.
- `outstring` and `outlstring` place string data into `ADATA` records, chunked by `NSNAME` and respecting suppression/alignment.
- `mulcon` consumes `mul.c` sequences to lower multiplication by constants into shifts/adds/subtracts.
- `nullwarn` warns on unused expression results while still generating side effects.
- `sextern` and `gextern` emit static/global data initializers.
- `outcode`, `zwrite`, `zname`, `zaddr`, and `outhist` serialize instructions, symbols, history, names, addresses, constants, and signatures to the object stream.
- `ieeedtod` encodes host doubles into Plan 9 IEEE words.
- `align` and `maxround` implement target-specific struct, argument, and automatic-storage alignment.

Dependencies and interactions:
- Uses output buffer `outbuf`, symbol tables, history records, and backend instruction stream.
- Called by statement/expression generation, global initialization, and final compiler cleanup.

Research relevance:
- This file covers several backend boundary concerns: switch code shape, object format emission, data layout, and constant multiply lowering.
