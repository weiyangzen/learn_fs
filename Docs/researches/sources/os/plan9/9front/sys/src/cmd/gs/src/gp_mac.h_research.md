# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mac.h

Small Mac platform support header.

Key contents:
- Include guard `gp_mac_INCLUDED`.
- Defines `HWND` as `int`.
- Declares `hwndtext`, used as a DLL/application instance identifier by Mac polling and callback code.

Research notes:
- This is a compatibility shim so code shared with Windows-style callback paths can compile on Mac.
