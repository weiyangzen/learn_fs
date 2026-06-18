# File Research: sources/os/plan9/9front/sys/src/cmd/iostats.c

Runs a command through a 9P proxy and reports filesystem I/O statistics.

Key points:
- Usage: `iostats [-dC] cmds [args ...]`.
- Creates a pipe-mounted namespace for the child command and runs `exportfs -r /` behind it.
- Duplicates original stdio fds so the child can keep stdin/stdout/stderr through the mounted namespace.
- Tracks 9P request and response messages:
  - decodes `Fcall`s with `convM2S`
  - matches responses to requests by tag
  - times each RPC with `nsec`
  - tracks protocol bytes in/out
- Maintains fid table mapping fids to qids and paths across attach, walk, open/create, clunk/remove.
- Tracks per-file opens, read counts/bytes, write counts/bytes.
- Handles child completion by posting a private `done` note to the filesystem proxy process.
- Prints total read/write/protocol throughput, RPC counts/timing, protocol byte counts, and per-file open/read/write summary.
- `-d` runs exportfs with debug; `-C` adds `MCACHE` mount flag.

Dependencies and interactions:
- Uses Plan 9 `mount`, `exportfs`, 9P `Fcall`, process namespace isolation, pipes, rfork shared memory, and notes.

Research relevance:
- Useful instrumentation code for observing 9P filesystem workloads at the protocol boundary.
