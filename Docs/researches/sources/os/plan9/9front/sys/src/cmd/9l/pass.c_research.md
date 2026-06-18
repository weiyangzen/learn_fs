# File Research: sources/os/plan9/9front/sys/src/cmd/9l/pass.c

This file implements major linker transformation passes after object loading: data layout, undefined-symbol checking, branch target resolution, code-follow ordering, numeric parsing, rounding, and import/export table construction.

Key routines:
- `dodata` validates data initializers, lays out small data, regular data, BSS, literal pools, and defines linker symbols such as `setSB`, `bdata`, `edata`, `end`, and `etext`.
- `undef` reports unresolved external references.
- `relinv` returns inverse conditional branch opcodes.
- `follow` and `xfol` reorder reachable code to improve fallthroughs and duplicate small branch islands where useful.
- `patch` resolves branch symbols to `Prog.cond` pointers and handles undefined dynamic imports via `UP`.
- `mkfwd` builds skip-forward pointers to speed branch target lookup.
- `brloop` collapses chains of unconditional branches.
- `atolwhex` parses decimal, octal, hex, and signed numeric options.
- `rnd` rounds values to alignment.
- `import`, `ckoff`, `newdata`, and `export` build dynamic import/export metadata and exported symbol tables.

Important interactions:
- Runs before `noops`, `span`, and `asmb`.
- Consumes symbols and data records from `obj.c`.
- Produces data layout consumed by `asm.c:datblk`.
- Dynamic import/export records feed `span.c:dynreloc` and `asmdyn`.

Research notes:
- Literal-pool insertion targets large `AMOVW` constants or symbol addresses that are not compactly encodable.
- `follow` rewrites control flow using `FOLL` marks and branch inversion for layout.
- Export table construction serializes signature, address, and name pointer triples into data records.
