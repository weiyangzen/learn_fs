# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printmap.c

Purpose: Prints the configured Venti index layout/map.

Key behavior:
- Parses `-B` but does not use the value.
- Forces read-only mode, loads the Venti config, and calls `printindex` on `mainindex`.

Dependencies:
- Uses `initventi`, global `mainindex`, and Venti index printing helpers.

Notable details:
- The local `fix` variable is always zero, so the tool always runs read-only.
