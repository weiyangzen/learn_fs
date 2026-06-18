# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/zip.c

Decompresses Mercurial revlog compressed chunks.

Key points:
- Defines a buffered input wrapper `struct zbuf` around a fd and remaining compressed length.
- `zgetc()` feeds bytes to Plan 9 `inflate()` from an in-memory buffer, refilling from the fd until the specified length is exhausted.
- `zwrite()` writes inflated bytes to an output fd.
- `funzip()` handles Mercurial revlog chunk prefixes:
  - `'\0'`: raw uncompressed data
  - `'u'`: uncompressed data with explicit marker
  - `'x'`: deflated data
  - anything else is rejected
- Copies raw chunks directly and inflates deflated chunks through `<flate.h>`.
- Returns written length or `-1` on failure.

Dependencies and interactions:
- Used by `revlogextract()` to unpack revlog base and delta chunks.
- Depends on Plan 9 `<flate.h>`.

Research relevance:
- Minimal revlog compression adapter for Mercurial’s per-chunk storage format.
