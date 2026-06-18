# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/cylequalarea.c

Read fully: 24 lines, 355 bytes. SHA-256 prefix: `72e41132551d3df2`.

Implements cylindrical equal-area projection parameterized by standard parallel. `cylequalarea(par)` rejects parallels over 89 degrees, computes scale `cos(par)^2`, and returns `Xcylequalarea`. The projection maps x to scaled longitude and y to sine latitude.

Risk notes: static scale `a` is shared globally.
