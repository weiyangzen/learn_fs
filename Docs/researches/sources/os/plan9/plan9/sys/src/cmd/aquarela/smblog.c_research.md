# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smblog.c

Logging and hex dump utilities for SMB diagnostics.

Key functions:
- `smbloglock` and `smblogunlock` provide nested logging locks.
- `smblogvprint`, `smblogprint`, `translogprint`, and `smblogprintif` conditionally print to configured log fd/stderr.
- `smblogdata` prints bounded hex/ASCII dumps.

Interactions:
- Used throughout packet receive/send and command handlers.

Notable details:
- `smblogprint` checks `smbtrans2optable[cmd].debug`; for ordinary SMB command ids this appears inconsistent with `translogprint` and can index beyond the transaction2 table for large command values.
