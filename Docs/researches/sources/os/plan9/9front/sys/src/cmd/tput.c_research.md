# File Research: sources/os/plan9/9front/sys/src/cmd/tput.c

Read completely: 72 lines, 1234 bytes.

Throughput meter. It reads stdin in a configurable buffer, optionally writes data to stdout, and a shared-memory child reports byte rate once per second.

Key behavior:
- `-b buflen` sets read buffer size; default is `iounit(0)` or `IOUNIT`.
- `-p` passes input through to stdout.
- `-w` reports a one-second windowed rate by atomically swapping byte count; otherwise reports cumulative average.
- Uses `rfork(RFPROC|RFMEM)` so the child sees shared atomic counters.

Reliability notes:
- The reporting child runs until killed by parent with `postnote`.
- Write errors in pass-through mode are not checked; read errors are fatal.
