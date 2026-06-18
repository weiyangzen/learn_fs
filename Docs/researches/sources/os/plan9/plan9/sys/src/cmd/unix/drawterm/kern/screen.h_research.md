# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/screen.h

This header defines shared screen, mouse, and cursor state for drawterm's hosted GUI backends.

Key contents:
- `Mousestate` stores buttons, point, and event timestamp.
- `Mouseinfo` stores a small ring buffer, lock, open/translation state, and rendezvous for mouse readers.
- `Cursorinfo` stores cursor offset plus clear/set masks.
- `Screeninfo` stores screen lock, pending soft screen image, reshape flag, depth, and DIB type.
- Declares global `gscreen`, `mouse`, `cursor`, and `screen`.
- Declares screen, cursor, mouse, color, flush, and draw-lock APIs.

Important details:
- Mouse queue capacity is fixed at `Mousequeue` 16, with one slot unused by ring-buffer convention.
- This header connects kernel draw device logic with platform GUI files.
