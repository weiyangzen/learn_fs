# File Research: sources/os/plan9/9front/sys/src/9/port/devpipe.c

Purpose: Implements `#|`, Plan 9 kernel pipes with two queue-backed endpoints, `data` and `data1`.

Key logic:
- `pipeattach` allocates a `Pipe`, two queues, and a unique qid namespace.
- `pipeopen` tracks per-end open counts and sets `iounit` to `qiomaxatomic`.
- Reads from one endpoint drain that endpoint’s queue; writes to one endpoint enqueue into the opposite queue.
- Closing the final open on either endpoint hangs up the opposite side and closes its own queue; when both sides close, queues are reopened for reuse.
- `pipewstat` uses the stat length field to set both queue limits, bounded by `conf.pipeqsize`.

Dependencies and integration:
- Uses Plan 9 `Queue` primitives (`qread`, `qwrite`, `qbread`, `qbwrite`, `qhangup`, `qclose`, `qreopen`) and net-style qid packing macros.

Risks and notes:
- Writes to a closed pipe post a user note unless the channel is marked `CMSG`, avoiding notes for mounted queues.
- Pipe queue size is rounded up to a multiple of the maximum atomic queue I/O unit.
