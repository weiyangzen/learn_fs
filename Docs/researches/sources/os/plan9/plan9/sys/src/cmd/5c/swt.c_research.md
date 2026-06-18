# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/swt.c

## Scope

Switch lowering, bit-field access, constant multiply expansion, object serialization, history emission, and alignment logic for `5c`.

## Behavior

- `swit1()`/`swit2()` lower switch statements to linear compares, binary-search branches, or dense `ACASE`/`ABCASE` jump tables.
- `bitload()` and `bitstore()` load, mask, shift, merge, and store C bit-fields.
- `outstring()` batches string data into `ADATA` records.
- `mulcon()` expands multiplication by selected constants using precomputed add/shift recipes.
- `outcode()` emits Plan 9 object records with symbol cache entries, `ANAME`/`ASIGNAME`, instruction encodings, and source history.
- `align()` implements ARM ABI-ish layout for structs, arguments, and automatics.

## Dependencies

Uses `gc.h`, `Biobuf`, compiler object format constants, `Node`, `Sym`, `Prog`, `Hist`, and floating conversion helpers.

## Risks And Invariants

- Object encoding uses small rolling symbol indices (`NSYM`); collisions are handled by re-emitting names.
- `zaddr()` uses fixed buffer assumptions sized for the largest encoded address.
- Dense switch selection is simple range-vs-count heuristics, not profile-aware.
- `align()` encodes little-endian behavior directly and has special pack-flag paths.
