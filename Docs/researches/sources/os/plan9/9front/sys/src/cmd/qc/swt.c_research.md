# File Research: sources/os/plan9/9front/sys/src/cmd/qc/swt.c

Switch lowering, bitfield helpers, string/global data emission, object serialization, and type alignment for the Power compiler backend.

Key responsibilities:
- `swit1`/`swit2` emit binary-search switch dispatch with linear fallback for small case counts.
- `bitload` and `bitstore` extract/update C bitfields using shifts and masks.
- `outstring`, `sextern`, and `gextern` emit string and global data, including vlong split emission.
- `mulcon` converts `mul.c` compact multiply recipes into instruction sequences.
- `outcode`, `zwrite`, `zname`, `zaddr`, and `outhist` serialize `Prog` lists into Plan 9 object format.
- `align`, `doubled`, and `maxround` implement Power ABI alignment for structs, arrays, parameters, automatics, and double-containing aggregates.

Dependencies and coupling:
- Shares object encoding conventions with `qa/lex.c`.
- Uses `txt.c` instruction emission helpers and `mul.c` constant multiply recipes.
- Depends on `Biobuf`, symbol signatures, and common history records.

Filesystem/OS relevance:
- Emits object file records and source history path records; no runtime filesystem logic.
