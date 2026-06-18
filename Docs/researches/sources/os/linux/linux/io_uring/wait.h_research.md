# File Research: sources/os/linux/linux/io_uring/wait.h

Header for completion wait and CQ event helpers.

Key responsibilities:
- Defines CQ wake sentinel values.
- Defines `struct ext_arg` for timeout, signal mask, minimum-time, and iowait options.
- Declares CQ wait, task_work signal run, and CQ overflow flush helpers.
- Provides inline kernel/user CQ event count helpers.

Important invariants:
- `IO_CQ_WAKE_INIT` is larger than any valid wait count so normal wake threshold comparisons fail when no waiter exists.
- `io_cqring_events()` includes a read barrier before reading cached CQ tail.
