# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/swt.c

Purpose: 386 C compiler support routines for switches, bitfields, object output, history records, and ABI alignment.

Key behavior: `swit1` emits linear or binary-search switch compare/jump chains. `bitload`/`bitstore` extract and update C bitfields. `outstring`, `gextern`, `outcode`, `zname`, and `zaddr` serialize compiler `Prog` streams and symbol references into Plan 9 object format. `outhist` writes source-history records. `align` and `maxround` implement 386 stack/struct/argument layout.

Integration notes: object encoding here is decoded by `8l/obj.c`; changes to `zaddr`/symbol table caching must remain compatible with linker `zaddr`. Alignment decisions drive generated ABI layout and stack frame sizes.
