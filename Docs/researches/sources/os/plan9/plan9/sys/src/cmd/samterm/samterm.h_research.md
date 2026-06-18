# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/samterm.h

Defines shared `samterm` structures, globals, and function prototypes.

Key types:
- `Section` is a rasp segment with rune count, optional text, and next pointer.
- `Rasp` tracks total runes and the section list.
- `Text` owns one file/command rasp, up to `NL` flayers, a protocol tag, lock count, and active front window.
- `Readbuf` is the host/plumb double-buffer payload.

Key constants and enums:
- `RUNESIZE`, `MAXFILES`, `READBUFSIZE`, `NL`, `Untagged`.
- Direction enum `Up`/`Down`.
- Resource enum `RHost`, `RKeyboard`, `RMouse`, `RPlumb`, `RResize`, `NRes`.

Behavior notes:
- Includes `mesg.h` with `SAMTERM` defined, so terminal code shares wire-protocol constants.
- Declares most cross-file UI, protocol, rasp, menu, scroll, and Plan 9 integration functions.
