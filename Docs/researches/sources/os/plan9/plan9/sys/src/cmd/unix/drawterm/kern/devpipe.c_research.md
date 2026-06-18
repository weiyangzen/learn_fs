# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devpipe.c

Implements Plan 9 pipe device `#|`.

Key behavior:
- A pipe has two queues and exposes `data` and `data1`.
- Writes to one end are read from the other end.
- Queue size defaults to 256 KiB on multiprocessor configurations, 32 KiB otherwise.
- Tracks references to the pipe and per-end open counts.
- Closing the final open reference on either side hangs up the opposite queue.
- Reopens queues when both ends are closed, making the pipe reusable until final channel references drop.
- Supports block read/write through `qbread` and `qbwrite`.

Important interfaces:
- Uses `NETQID`, `NETID`, and `NETTYPE` macros from `netif.h` for qid layout.
- `pipedevtab` registers device character `|`.

Notable risks:
- Write errors post a user note `"sys: write on closed pipe"` unless the channel is a mounted message channel.
