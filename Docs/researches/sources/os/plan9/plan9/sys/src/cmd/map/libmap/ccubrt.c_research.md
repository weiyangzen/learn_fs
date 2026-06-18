# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/ccubrt.c

Read fully: 13 lines, 226 bytes. SHA-256 prefix: `044aa388b848b109`.

Provides `ccubrt()`, a complex cube-root helper. It converts input to polar form, cube-roots the radius using `cubrt()`, divides angle by three, and returns rectangular coordinates.

Integration: used by advanced projections such as `hex.c`.

Risk notes: returns one principal cube root only.
