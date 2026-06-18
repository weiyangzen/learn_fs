# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/mul.c

Purpose: generate shift/add/subtract sequences for multiplication by integer constants.

Core behavior:
- `mulcon0` returns a cached `Multab` sequence for an absolute constant.
- It first checks a cache, then a sorted exception `hintab`, then searches for short sequences, then tries recursion plus trailing shifts.
- Encoded sequences use letters for shifts and `+`/`-` operations with operand selectors.
- `docode`, `gen1`, `gen2`, and `gen3` search and validate sequence encodings.
- `hintab` stores constants where the search algorithm fails or benefits from precomputed sequences.

Integration points:
- `swt.c` uses `mulcon0` via `mulcon` to optimize `OMUL`/`OLMUL` by constants.
- `gc.h` declares `Multab`/`Hintab`.

Risks:
- Dense recursive search and compact sequence encoding are difficult to audit.
- Constants outside successful search/hint paths fall back to hardware multiply.
- Hint table ordering is required for binary search.
