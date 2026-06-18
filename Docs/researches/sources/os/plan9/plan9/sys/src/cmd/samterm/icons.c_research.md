# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/icons.c

Defines cursor bitmaps and initializes a shared color.

Key contents:
- `bullseye`, `deadmouse`, and `lockarrow` Plan 9 `Cursor` bitmaps.
- `darkgrey` image for UI drawing.
- `iconinit` allocates `darkgrey` as a 1x1 image.

Behavior notes:
- Cursor objects are global and referenced by terminal UI state, especially lock/error states.
