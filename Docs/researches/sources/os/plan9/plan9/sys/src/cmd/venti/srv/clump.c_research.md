# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/clump.c

Provides clump write and read primitives. A Venti clump is the immutable on-disk record containing a header plus compressed or uncompressed lump data.

`storeclump()` validates size and type, optionally checks the caller-provided score, compresses with `whackblock()`, fills a `Clump` header, appends the clump through `writeiclump()`, and returns an `IAddr` suitable for indexing.

`clumpmagic()` reads the clump magic at an arena-relative address. `loadclump()` reads enough arena blocks, unpacks the clump header, rejects corrupt-marker clumps, reads more data if the caller's block estimate was too small, decompresses when needed, and optionally verifies score and type.

The file bridges raw arena append storage and score-address index records, with SHA1 score verification as the main integrity check.
