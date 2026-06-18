# File Research: sources/os/plan9/plan9/sys/src/cmd/tee.c

Plan 9 `tee` implementation.

Key responsibilities:
- Parses `-a`, `-i`, and ignored legacy `-u`.
- Opens or creates each output file, appending when `-a` is set.
- Always includes stdout as the final output target.
- Copies stdin to all open outputs using an 8192-byte buffer.
- Installs a note handler for `-i` that ignores interrupt notes.

Notable behavior:
- Write errors are ignored after opening; the loop exits only on read EOF or read error.
- Append mode opens existing files write-only and seeks to end, otherwise creates them.
