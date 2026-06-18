# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/gilbert.c

Read fully: 51 lines, 1210 bytes. SHA-256 prefix: `13808efe85fa2561`.

Implements Gilbert projection. `Xgilbert()` maps the sphere to a hemisphere by transforming latitude via `tan(lat/2)` and longitude by half, clamps transformed sine to `[-1,1]`, then presents the hemisphere orthographically. `gilbert()` returns this projection function.

The file includes a derivation comment explaining stereographic projection to plane, square root mapping to a half plane, and inverse stereographic projection.

Risk notes: always returns success and does not clip by hemisphere edge beyond internal clamp.
