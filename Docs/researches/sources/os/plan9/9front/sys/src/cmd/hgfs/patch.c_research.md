# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/patch.c

Applies Mercurial binary delta patches to reconstruct revlog contents.

Key points:
- `fcopy()` copies a range from one fd to another, supporting bounded or until-EOF copy.
- Defines a 12-byte all-`0xff` patch marker used to separate patch streams.
- `fpatchmark()` writes that marker.
- `fpatch()` builds a linked list of fragments representing base file ranges and patch-inserted data.
- Reads patch records as 12-byte big-endian triples:
  - start
  - end
  - inserted length
- Maintains Mercurial patch offset adjustment as patches are applied.
- Splits, trims, or removes existing fragments overlapped by the patch range.
- Inserts new fragments pointing into the patch file.
- Finally copies fragment sequence to output.
- Frees all fragment records on success or failure.

Dependencies and interactions:
- Used by `revlogextract()` after compressed delta chunks are decompressed.
- Works with temp files created by `fmktemp()`.

Research relevance:
- Core delta-application logic needed to materialize Mercurial revlog revisions.
