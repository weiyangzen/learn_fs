# File Research: sources/os/plan9/plan9/sys/src/cmd/dial/pass.c

This file implements an interactive pass-through helper for one line of console/modem exchange.

Key behaviors:
- Usage: `pass [-q]`.
- Opens `/dev/cons` for console I/O and enables raw mode through `/dev/consctl` when available.
- Uses `rfork(RFPROC|RFFDG|RFMEM)` so parent and child share globals.
- Parent reads stdin one byte at a time with a short alarm and echoes to console unless quiet.
- Child reads one console line and writes it to stdout.
- Stops when a newline/carriage return is seen or when the shared `done` flag is set.

Notable implementation details:
- `ding()` is installed with `notify()` and turns alarm notes into resumable interruptions.
- Shared globals `alarmed` and `done` coordinate parent/child shutdown.
- The helper is designed for half-duplex scripted interaction where a user supplies one line.
