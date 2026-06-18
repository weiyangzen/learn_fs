# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/kbdv.c

## Role

`kbdv.c` converts local Plan 9 keyboard input into VNC key events for the viewer.

## Main Behavior

- Maps Plan 9 special runes to X11 keysyms through `ktab`.
- Uses `utf2ksym.h` to convert Unicode runes to X11 keysyms where needed.
- `keyevent()` writes `MKey` messages with key symbol and down/up state.
- `readcons()` is a fallback path for systems without `/dev/kbd`; it opens `display->devdir/cons`, enables raw mode, tracks toggled modifiers, and sends key down/up pairs.
- `readkbd()` reads structured `/dev/kbd` records and sends key down/up events based on `k`, `K`, and `c` records.
- `runetovnc()` converts a Plan 9 rune to the keysym value sent to the remote server.

## Notable Limitations And Risk Areas

- Modifier handling differs between `/dev/kbd` and raw console fallback.
- Uppercase and shifted punctuation may synthesize a shift press for compatibility with some servers.
- Control-character handling emits explicit control key press/release sequences.
- The code intentionally suppresses character events when modifier keys are active in the `/dev/kbd` path.
