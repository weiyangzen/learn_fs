# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/icons.c

Small RISC OS GUI utility module for updating WIMP icons.

Functions:

- `vUpdateIcon()` redraws an icon through `Wimp_UpdateWindow`, `Wimp_PlotIcon`, and `Wimp_GetRectangle`.
- `vUpdateRadioButton()` checks current selected state and toggles the RISC OS selected flag if needed.
- `vUpdateWriteable()` writes a string into an indirected text icon, keeps the caret at the end when focused, and redraws.
- `vUpdateWriteableNumber()` formats an integer and delegates to `vUpdateWriteable()`.

The file is GUI-only and does not participate in document parsing. It depends on DeskLib WIMP APIs and Antiword error helpers.
