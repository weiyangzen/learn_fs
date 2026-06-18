# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/azequalarea.c

Read fully: 19 lines, 274 bytes. SHA-256 prefix: `f554c2aa78749b73`.

Implements azimuthal equal-area projection. `Xazequalarea()` computes radius `sqrt(1 - sin(latitude))` and maps west longitude sine/cosine to x/y. `azequalarea()` returns the projection function.

Dependencies: caller supplies normalized `struct place` with precomputed sine/cosine fields.

Risk notes: no parameter state and always returns success.
