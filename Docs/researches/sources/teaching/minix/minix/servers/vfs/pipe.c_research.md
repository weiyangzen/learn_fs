# File Research: sources/teaching/minix/minix/servers/vfs/pipe.c

Implements pipe creation, pipe/FIFO feasibility checks, suspension, revival, and signal interruption for blocked VFS calls.

Key behavior:
- `do_pipe2` combines modern flags and backward-compatible flags, calls `create_pipe`, and returns the fd pair.
- `create_pipe` locks PipeFS, allocates a vnode, gets two filps/fds, creates a PipeFS node with `REQ_NEWNODE`, fills vnode mapping fields, and assigns read/write filps.
- `map_vnode` maps named FIFOs to PipeFS by creating a temporary PipeFS node and storing `v_mapfs_e`, `v_mapinode_nr`, and map reference count.
- `pipe_check` determines whether pipe reads/writes can proceed, should suspend, should fail with `EAGAIN/EPIPE`, or should perform a partial write. It wakes opposite-side waiters through `release` when state changes.
- `suspend` marks the current process blocked and updates `susp_count` for pipe open/pipe I/O blocks.
- `pipe_suspend` stores resumable read/write state in `fp_pipe`.
- `release` wakes blocked pipe open/read/write callers and notifies select waiters on matching pipe filps.
- `revive` either marks pipe/flock waiters for main-loop revival or replies immediately for select/cdev/popen states.
- `unpause` handles signal interruption across pipe, flock, select, popen, cdev, and sdev blocking states.

Important dependencies:
- Pipe data I/O is performed later by `read.c` through mapped PipeFS inode requests.
- Select integration uses `select_callback`.
- Socket-driver blocking is delegated to `sdev_cancel` and `sdev_stop`.

Notable implementation details:
- Pipe writes larger than `PIPE_BUF` may be partially written and then suspended for remaining data.
- `revive` deliberately rejects `_SDEV` because socket cleanup is handled in `sdev.c`.
