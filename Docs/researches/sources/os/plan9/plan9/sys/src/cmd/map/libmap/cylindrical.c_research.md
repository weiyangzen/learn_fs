# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/cylindrical.c

Read fully: 19 lines, 287 bytes. SHA-256 prefix: `4d14a8a65239a8a6`.

Implements a simple cylindrical projection. `Xcylindrical()` rejects latitudes beyond 80 degrees, maps x to negative longitude, and y to tangent latitude (`sin/cos`). `cylindrical()` returns that function.

Risk notes: returns `-1` for rejected high-latitude points; caller must handle that status.
