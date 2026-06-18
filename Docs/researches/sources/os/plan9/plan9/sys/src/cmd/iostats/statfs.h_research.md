# File Research: sources/os/plan9/plan9/sys/src/cmd/iostats/statfs.h

`statfs.h` is the shared contract for the iostats 9P proxy.

Key contents:
- Constants for debug file, process limits, fid hash size, max data size, max RPC array size, work buffer count, and fid chunking.
- Defines:
  - `Frec` for per-file aggregate opens/reads/writes/bytes.
  - `Rpc` and `Stats` for per-message timing and byte counters.
  - `Fsrpc` as a work item containing one `Fcall`, buffer, pid, busy/interrupt/flush state.
  - `Fid` as active fid state, backing fd, file pointer, counters, and directory offset.
  - `File` as cached tree node with qid and parent/child links.
  - `Proc` as blocking slave process state.
- Declares globals through `Extern`.
- Declares 9P service handlers and shared helpers.

Important dependencies:
- Consumed by both `iostats.c` and `statsrv.c`; `Extern` controls definition vs declaration.

Notable risks/quirks:
- `Maxrpc` is 20000 even though normal 9P message type ids are sparse and small.
