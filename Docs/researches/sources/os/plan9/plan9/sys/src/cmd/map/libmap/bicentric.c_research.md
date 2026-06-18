# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/bicentric.c

Read fully: 25 lines, 437 bytes. SHA-256 prefix: `ffb50f5a8e758d6f`.

Implements bicentric projection parameterized by an angle `l`. `bicentric()` rejects near-polar parameters over 89 degrees, stores the center coordinate, and returns `Xbicentric`. The projection rejects points near longitude or latitude cosine zero, computes x/y by tangent-like formulas, and returns whether the point lies within radius-squared 9.

Risk notes: static `center` means one active parameterization at a time.
