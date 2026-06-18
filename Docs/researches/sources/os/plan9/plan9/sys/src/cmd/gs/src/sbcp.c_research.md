# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbcp.c

Implementation of Ghostscript BCP and TBCP stream filters.

The encode side escapes selected control characters by writing `CtrlA` and XORing the character with `0x40`. Two escape tables distinguish BCP from TBCP; TBCP additionally escapes ESC.

The decode side tracks escape state and handles protocol control characters:

- `CtrlA`: starts an escaped control byte.
- `CtrlC`: calls the client `signal_interrupt` callback.
- `CtrlD`: signals end of data unless escaped.
- `CtrlT`: calls the client `request_status` callback.
- `CtrlE`, `CtrlQ`, `CtrlS`, and `Ctrl-\`: ignored protocol controls.
- TBCP-specific escaped `[` and `M` handling.

It defines stream templates for `BCPEncode`, `TBCPEncode`, `BCPDecode`, and `TBCPDecode`.

This is printer/job transport encoding support for Ghostscript streams. It is not filesystem code.
