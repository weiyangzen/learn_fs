# File Research: sources/os/plan9/9front/sys/src/cmd/plumb/fsys.c

`fsys.c` implements the plumber’s 9P file server. It exposes a directory with `rules`, `send`, and dynamic plumb-port files; posts a `/srv` endpoint; mounts itself at `/mnt/plumb`; and manages fid state, open-port lists, read queues, send queues, held messages, and partial writes.

Writes to `send` unpack plumb messages, run them through rule sets, rewrite/deliver/start clients as needed, and queue messages to destination ports. Reads from port files block by queuing read requests until a send can be drained. Opening a port transfers held messages, and closing a port removes pending sender references for that fid.

The `rules` file supports exclusive write access, truncation to clear current rules, incremental parsing via `writerules()`, and readback via `printrules()`. The implementation uses locks around shared queues and a small process pool around 9P reads.
