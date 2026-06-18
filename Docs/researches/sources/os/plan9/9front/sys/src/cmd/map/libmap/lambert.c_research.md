# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/lambert.c

Implements Lambert conformal conic projection with two standard parallels. It normalizes parameter order, falls back to Mercator for opposing parallels and perspective/stereographic-like behavior for equal parallels, rejects near-pole parameters, computes cone constant `k`, and maps latitude/longitude in `Xlambert()`.

The projection rejects far-southern points and has a special case for near north pole radius zero.
