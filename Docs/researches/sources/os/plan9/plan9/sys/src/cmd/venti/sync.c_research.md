# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/sync.c

Purpose: Client utility that sends a Venti sync request.

Key behavior:
- Connects to a Venti server, performs `vtconnect`, optionally calls `vtsync`, then hangs up.
- `-h` selects host; hidden `-x` sets `donothing` and skips `vtsync`.

Dependencies:
- Uses libventi client APIs and Plan 9 thread main.

Notable details:
- Installs Venti score and fcall formatters for diagnostics.
