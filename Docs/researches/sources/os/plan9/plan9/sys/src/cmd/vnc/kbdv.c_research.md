# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/kbdv.c

VNC client-side keyboard sender from local Plan 9 keyboard input to RFB key events.

Key responsibilities:
- Reads raw keyboard runes from the display console.
- Maps Plan 9 special keys and function keys to X keysyms.
- Uses `utf2ksym.h` to translate Unicode runes to X keysyms when possible.
- Sends RFB key-down/key-up messages.
- Synthesizes modifier events for Alt, Control, Shift, control-letter combinations, uppercase letters, and shifted punctuation.

Important behavior:
- Opens display `cons` and `consctl`, then enables raw mode.
- Modifier keys toggle local state; ordinary keys are sent down then up.
- After a normal key, any active Alt/Ctrl/Shift is released.
- Adds temporary Shift for characters known to need it on some VNC servers.

Risks:
- Modifier state toggling depends on Plan 9 keyboard rune behavior, not physical key up/down.
- Fatal exits on console read failure.
