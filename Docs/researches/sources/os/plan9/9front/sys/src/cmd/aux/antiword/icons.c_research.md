# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/icons.c

This file contains RISC OS Wimp icon update helpers.

Key routines:
- `vUpdateIcon(...)` redraws a window icon over update rectangles.
- `vUpdateRadioButton(...)` toggles selected state and redraws only if the requested state differs.
- `vUpdateWriteable(...)` updates indirected text in a writable icon and moves the caret to the end if needed.
- `vUpdateWriteableNumber(...)` formats an integer and delegates to `vUpdateWriteable`.

Important behavior:
- Requires writable icons to be indirected text.
- Uses `Error_CheckFatal` around Wimp calls.
- Maintains caret position for active edited icons.

Dependencies:
- DeskLib Wimp APIs and antiword error/debug helpers.

Role in antiword:
- Supports the RISC OS GUI choices and controls.
