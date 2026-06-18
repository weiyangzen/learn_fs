# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/conswdir.c

This file filters console output for xterm-style title escape sequences that encode working-directory changes.

Key behavior:
- Detects sequences of the form ESC `] ; path` BEL.
- Removes those in-band messages from the byte stream passed to stdout.
- Runs `/bin/rwd` or a supplied program with the extracted path.
- Saves and restores `/dev/label` and `/dev/wdir`.

Important details:
- Uses a small state machine over buffered input.
- Gives up and passes bytes through if an escape sequence grows too long without termination.
- Handles interrupts by continuing and restores state on exit.

Filesystem relevance:
- Indirect: updates Plan 9 window/device state via `/dev/label` and `/dev/wdir`.
