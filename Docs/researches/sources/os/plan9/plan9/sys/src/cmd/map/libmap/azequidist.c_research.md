# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/azequidist.c

Read fully: 19 lines, 290 bytes. SHA-256 prefix: `a23ad7335c8caf1d`.

Implements azimuthal equidistant projection. `Xazequidistant()` computes colatitude and maps it by west longitude sine/cosine. `azequidistant()` returns the projection function.

Risk notes: no clipping or failure cases; assumes normalized coordinates.
