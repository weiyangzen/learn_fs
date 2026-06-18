# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zpacked.c

## Purpose
Implements PostScript packed-array operators and the packed-array construction routine.

## Key Functions
- `zcurrentpacking()` returns current array-packing mode.
- `zpackedarray()` builds a packed array from stack operands.
- `zsetpacking()` changes packing mode.
- `make_packed_array()` packs names, small integers, and executable operators into compact storage.

## Important Behavior
- `packedarray` validates count against operand-stack depth and pops source elements on success.
- Packing checks local-into-global store constraints.
- Mixed arrays use full refs for un-packable elements while preserving packed refs around them.
- Alignment padding uses legal packed refs so the garbage collector can scan storage.
- Result arrays are read-only and created as shortarray or mixedarray depending on contents.

## Research Notes
Low-level memory/representation code for compact PostScript procedure storage.
