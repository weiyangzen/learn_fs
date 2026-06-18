# File Research: sources/os/plan9/9front/sys/src/cmd/tee.c

This is Plan 9 `tee`, copying stdin to stdout and all named files.

Behavior:
- `-a` appends by opening existing files or creating them, then seeking to end.
- `-i` installs a notify handler that ignores `"interrupt"`.
- `-u` is accepted but ignored as an undocumented Unix relic.
- Files are duplicated onto descriptors starting at `FDSTART` (`3`) and written sequentially for every input block.

Risk notes:
- Write errors are ignored after files are opened; a later failed file or stdout write does not affect exit status.
- Open failures are reported but do not stop copying to other destinations.
