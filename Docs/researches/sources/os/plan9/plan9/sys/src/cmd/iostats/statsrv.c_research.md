# File Research: sources/os/plan9/plan9/sys/src/cmd/iostats/statsrv.c

`statsrv.c` implements the iostats proxy 9P server handlers.

Key behavior:
- Handles version/auth/flush/attach/walk/create/clunk/remove/stat/wstat directly.
- Uses `slave` and `blockingslave` to run blocking open/read/write operations in worker processes.
- `okfile` blocks unsafe/special paths like most `/fd`, `/net/ssl`, `/net/tls`, and writable `/srv`.
- `update` accumulates per-RPC latency stats.
- `Xwalk` maintains the synthetic file tree and qids.
- `slaveopen`, `slaveread`, and `slavewrite` perform real filesystem I/O and update totals plus fid counters.
- Flush handling can interrupt workers via notes and defer flush replies.

Important dependencies:
- Uses globals from `statfs.h` and reply/path/fid helpers from `iostats.c`.

Notable risks/quirks:
- Comments acknowledge races due to no locks around some shared fid/open state.
- Directory reads maintain sequential offset state and reject nonzero offset jumps.
