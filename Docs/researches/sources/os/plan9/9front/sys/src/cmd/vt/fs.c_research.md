# File Research: sources/os/plan9/9front/sys/src/cmd/vt/fs.c

Synthetic 9p `/dev/cons` and `/dev/consctl` implementation for the `vt` terminal emulator. It mounts a private service before the host command starts so the command reads and writes through channels connected to the emulator.

Key behavior:
- `mountcons()` creates a 9p tree with `cons` and `consctl`, then posts it on `/dev` with `MBEFORE`.
- `fsreader()` pairs pending 9p reads with strings from `hc[0]`, handles flushes, copies partial data into the read reply, and drains queued host-input chunks.
- Writes to `cons` are converted from UTF bytes to `Rune` arrays with partial-rune carry state stored in the fid aux field, then sent to `hc[1]`.
- Writes to `consctl` toggle raw, hold, and winch state in the shared `Consstate`.
- Destroying an open `consctl` fid clears raw/hold/winch state; destroying any fid frees partial UTF state.

Notable dependencies:
- Plan 9 libthread/lib9p APIs: `Req`, `Fid`, `Srv`, channels, `threadpostmountsrv`.
- Shared terminal state and host channels from `cons.h` and `vt/main.c`.

Research notes:
- This file is the filesystem bridge for `vt`, not a persistent filesystem.
- `fsend()` sends a nil `Rune*` through `hc[1]`, which the UI side treats as host closure.
