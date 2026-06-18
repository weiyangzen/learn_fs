# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/elco2.c

Read fully: 132 lines, 2533 bytes. SHA-256 prefix: `7835c6d81b1fb145`.

Implements a complex elliptic integral routine based on Bulirsch, plus helpers `cdiv2()` and `csqr()`. `elco2()` computes an integral from `0` to `x+iy` with parameters `kc`, `a`, and `b`, returning success/failure and output `u,v`. It rejects `kc==0` or negative `x`, handles sign of `y`, iterates arithmetic-geometric style updates until `k <= CC`, and combines stored correction terms.

Integration: used by projections such as Guyou and hex that map through elliptic functions.

Risk notes: fixed arrays of 13 correction terms assume convergence before overflow. Accuracy near branch points is documented as reduced.
