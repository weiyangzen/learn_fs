# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/swt.c

This file combines switch lowering, bitfield access, string/global data emission, object serialization, and target alignment.

`swit1()`/`swit2()` lower switch cases into either linear comparisons for small case sets or a recursive binary decision tree. `bitload()` and `bitstore()` implement signed/unsigned bitfield extraction and insertion with masks and shifts.

`outstring()` emits fixed-size string chunks as `ADATA` records. `mulcon()` uses `mulcon0()` from `mul.c` to replace constant multiplication with shift/add/sub sequences. `gextern()` emits global initializer data, including 64-bit constants in target byte order.

`outcode()`, `zwrite()`, `zname()`, `zaddr()`, and `outhist()` serialize the generated `Prog` list into Plan 9 object records with rotating symbol slots and source history.

`align()` defines SPARC ABI layout for structs, arguments, and automatics, including big-endian parameter adjustment. This is a major ABI correctness point.
