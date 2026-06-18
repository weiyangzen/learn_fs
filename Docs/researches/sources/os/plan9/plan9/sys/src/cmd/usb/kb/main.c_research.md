# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/kb/main.c

Command entry point for USB keyboard/mouse support.

Behavior:
- Parses `-a` acceleration, `-d` USB debug, `-k` keyboard-only, `-m` mouse-only, `-N` ignored device number, and `-b` force boot protocol.
- Builds a worker argument string and chooses CSP matches for boot keyboard and pointer devices.
- If keyboard-only is requested, removes pointer CSP from the search list.
- Installs USB device formatter and calls `startdevs` with `matchdevcsp` and `kbmain`.

The file contains no event handling; it discovers devices and dispatches them to `kb.c`.
