# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/fisheye.c

Read fully: 26 lines, 407 bytes. SHA-256 prefix: `349760d971b8188d`.

Implements a refractive fisheye projection. `fisheye(par)` stores refractive parameter `n` and rejects values below `0.1`. `Xfisheye()` computes `u = sin(pi/4 - lat/2)/n`, rejects near-limit values, maps through `tan(asin(u))`, and projects by longitude sine/cosine.

Risk notes: static parameter `n`; returns `-1` when outside projection domain.
