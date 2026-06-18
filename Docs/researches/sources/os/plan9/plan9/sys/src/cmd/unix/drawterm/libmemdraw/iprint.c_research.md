# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/iprint.c

Stub internal print function.

Key function:
- `iprint`: marks its format argument used and returns `-1`.

Meaning:
- Provides a link-time placeholder for debug print calls in the library when no real kernel-style `iprint` is available.
