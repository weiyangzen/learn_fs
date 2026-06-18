# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ztype.c

## Purpose
Implements type inspection, executable/literal conversion, access restriction/check operators, and numeric/string/name conversions.

## Public Surface
- Exported for other interpreter components: `zcvx`, `zreadonly`, `zcvi`, `zcvr`.
- Registered operators: `cvi`, `cvlit`, `cvn`, `cvr`, `cvrs`, `cvs`, `cvx`, `executeonly`, `noaccess`, `rcheck`, `readonly`, `.type`, `.typenames`, `wcheck`, `xcheck`.

## Implementation Notes
- `.type` indexes type-name array by base type; structure refs derive names from registered structure type metadata.
- `.typenames` pushes executable name refs for known ref types and nulls for missing entries.
- `cvlit` clears executable; `cvx` sets executable but rejects internal operators outside the execution stack.
- Access checks use dictionary access refs when needed and apply `ref_save` before mutating dictionary access.
- `noaccess` rejects permanent dictionaries and read-only dictionaries.
- `cvi`/`cvr` accept numbers or strings tokenized by `scan_string_token`.
- `cvrs` supports radix 2..36 with custom integer conversion; radix 10 uses the shared object-to-string path.
- `cvs` uses `obj_cvs` and has a compatibility fallback that truncates selected operator names on rangecheck.

## Dependencies
Uses scanner utilities, dictionary stack checks, names, object conversion helpers, memory/ref root interfaces, and stream/filter headers required by scanner code.

## Risks and Notes
- Access mutation is security-sensitive and must preserve PostScript invalidaccess behavior.
- `cvx` deliberately protects internal operators from executable exposure.
- Real-to-int conversion uses conservative min/max real bounds.
- Filesystem relevance: none directly.
