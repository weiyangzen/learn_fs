# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfinp.h

Declarations for TrueType input helpers.

Key points:
- Declares byte, signed-byte, unsigned-short, unsigned-int, signed-short, and signed-int reader helpers.
- Assumes `ttfReader` is already declared by `ttfoutl.h`.

Dependencies and interactions:
- Used by TrueType parser code needing typed big-endian reads.

Research relevance:
- Thin header for the TrueType reader convenience API.
