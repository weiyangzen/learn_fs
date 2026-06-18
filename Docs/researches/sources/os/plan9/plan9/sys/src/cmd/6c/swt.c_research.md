# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/swt.c

This file handles switch lowering, bitfield access, string/data emission helpers, and final object output support.

`swit1` emits a binary-search comparison tree for switch cases, using direct linear compares for small case counts. `bitload` and `bitstore` load, mask, shift, merge, and store C bitfields while preserving signedness and unsigned extraction behavior.

`outstring` buffers string literals into `ADATA` records of `NSNAME` chunks. `gextern` emits global/static initialization data, converting address-like operands into `D_ADDR` records where needed.

`outcode`, `zname`, `zaddr`, and `outhist` write the compiler’s in-memory `Prog` list into Plan 9 object format, including source history, symbol table entries, compact address fields, 64-bit offsets, floating constants, and string constants.

The file also defines target alignment behavior for structs, arguments, and autos. Filesystem relevance is object generation and ABI layout: C structures and globals in OS/filesystem code rely on these size/alignment and object-emission rules.
