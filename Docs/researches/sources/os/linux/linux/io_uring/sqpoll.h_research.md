# File Research: sources/os/linux/linux/io_uring/sqpoll.h

Header defining SQPOLL shared state and lifecycle helpers.

Key responsibilities:
- Defines `struct io_sq_data`, including refs, park state, lock, ctx list, thread pointer, waitqueue, idle timeout, CPU/pid metadata, work time, state bits, and exit completion.
- Declares SQPOLL create, finish, stop, park/unpark, ref put, SQ wait, affinity, and CPU-time helpers.
- Provides `sqpoll_task_locked()` for RCU-protected thread lookup under lockdep.

Important invariant:
- `sqpoll_task_locked()` must be called with `sqd->lock` held.
