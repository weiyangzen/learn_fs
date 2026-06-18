# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/hwdraw.c

Stub hardware draw hook.

Key function:
- `hwdraw`: accepts a `Memdrawparam*`, marks it used, and returns `0`.

Meaning:
- No hardware-accelerated drawing is provided in this drawterm build; the core draw engine always falls through to software paths.
