# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/elliptic.c

Read fully: 35 lines, 627 bytes. SHA-256 prefix: `40febc9261cdbfdc`.

Implements an elliptic projection parameterized by longitude separation `l`. `elliptic(l)` rejects over 89 degrees, returns azimuthal equidistant for under 1 degree, otherwise stores `center` and returns `Xelliptic`. The projection computes two angular distances, derives x from squared-distance difference and y from remaining squared-distance sum, preserving hemisphere sign.

Risk notes: `center` is a global `struct coord`, not static, so it may be externally visible.
