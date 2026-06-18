# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/bbox.c

Bounding-box accumulation and transformation utilities for PostScript translators.

Key responsibilities:
- Maintains per-page `bbox` and whole-document `docbbox`.
- Tracks a current transformation matrix.
- Adds covered points, transforms boxes, writes DSC bounding-box comments, and resets page state.
- Provides `scale`, `translate`, `rotate`, and `concat`.

Important behavior:
- `writebbox()` transforms all four user-space corners through `ctm`, expands by `slop + .5`, writes integer bounds, then updates/reset document state.
- Whole-document `%%BoundingBox:` output uses saved `docbbox`.
- `resetbbox()` only updates document bounds when output went to stdout.

Dependencies:
- Uses `comments.h`, `gen.h`, and `ext.h`.

Notable risks:
- Global matrix/bbox state is not reentrant.
- Integer truncation after slop may under/overestimate for negative coordinates.
