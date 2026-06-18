# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/cursor.h

Minimal Plan 9 cursor bitmap structure.

Key contents:
- Defines `struct Cursor` with hotspot offset plus 16x16 `clr` and `set` bitplanes.

Role in this group:
- Used by GUI backends to translate Plan 9 cursor state into platform-native cursors.

Notable risks:
- Fixed 16x16 cursor representation; host cursor systems with different native sizes need adaptation.
