# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/main.c

User-mode cwfs entry point, process setup, memory/config initialization, server loops, readahead worker, dump worker, sync worker, and utility functions.

Key responsibilities:
- Provides console output helpers (`puts`, `putstrn`, `prflush`), `panic()`, and `okay()`.
- `mapinit()` reads a device map file mapping source device expressions to files or alternate devices.
- `confinit()` sets default resource sizes, calls `localconfinit()`, derives `nwpath`, `nauth`, and `gidspace`, and loads device mappings.
- `maxsize()` computes maximum representable file size from direct/indirect fanout with overflow checks.
- `printsizes()` reports block size, max file size, indirect fanout, cache bucket entries, and structure sizes.
- `main()` parses flags:
  - `-a` announce address
  - `-c` new cache layout
  - `-f` configure first
  - `-m` device map
  - one required config-device expression.
- Initializes queues, message buffers, networking, SCSI, file table, path table, uid/gid tables, auth, iobufs, config, system devices, and worker processes.
- `rahead()` consumes sorted readahead requests and warms block cache.
- `serve()` receives network 9P messages, detects protocol, dispatches protocol handlers, and frees messages.
- `exit()` marks active exiting, prints halt time, posts a note to process group, exits.
- `nextdump()` computes next automatic dump time.
- `wormcopy()` periodically copies pending dump blocks and triggers scheduled automatic dumps.
- `synccopy()` continuously flushes dirty blocks.
- `inqsize()` reads sd ctl geometry to discover sector size.

Important interactions:
- Uses configuration defaults from variant `conf.c`.
- Starts `netstart()`, `serve()`, `rahead()`, `wormcopy()`, `consserve()`, then runs `synccopy()` in the main process.
- Uses `fsprotocol[]` to sniff incoming protocol.

Research notes:
- The program is user-mode but uses old file-server architecture concepts: workers, queues, channels, and server-wide locks.
- `conf.mem = meminit()` uses available user memory estimates from `pc.c`; `iobufinit()` consumes most of it for block buffers.
- `serve()` only calls `cp->protocol(mb)` in the `else` branch after a protocol is already set. On the packet that first detects a protocol, it sets the protocol but does not dispatch in that same branch.
