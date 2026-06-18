# File Research: sources/os/plan9/9front/sys/src/cmd/kc/swt.c

Mixed backend support file covering switch lowering, bitfields, string/data emission, final object serialization, and type alignment. `swit1`/`swit2` emit binary-search switch dispatches with direct small-constant comparisons where possible. `bitload` and `bitstore` generate masking/shifting sequences for signed and unsigned bitfields.

`mulcon` consumes `mul.c` sequences to replace integer multiply-by-constant with shifts/add/subs. `outcode`, `zwrite`, `zname`, `zaddr`, and `outhist` serialize the final instruction stream and history records. `gextern`, `sextern`, and `outstring` generate initialized data records. `align` and `maxround` encode SPARC ABI layout and stack/argument alignment policy.
