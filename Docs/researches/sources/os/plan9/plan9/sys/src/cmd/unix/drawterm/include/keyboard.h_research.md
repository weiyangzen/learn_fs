# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/keyboard.h

Plan 9 keyboard control and private key constant header.

Key contents:
- Defines `Keyboardctl` with channel and console/ctl file state.
- Declares keyboard initialization/control/close functions.
- Defines Plan 9 private Unicode-space constants for function keys, navigation keys, insert/end, and modifier pseudo-keys.

Role in this group:
- GUI backends translate platform keyboard events into these runes before writing to `kbdq`.

Notable risks:
- `Kdown` and `Kview` share `Spec|0x00`, matching Plan 9 convention but easy to misread as a collision.
