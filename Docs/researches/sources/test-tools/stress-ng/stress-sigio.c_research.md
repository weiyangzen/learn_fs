# sources/test-tools/stress-ng/stress-sigio.c

Purpose: implements the `sigio` stressor, using asynchronous I/O notification on a pipe to generate SIGIO while a child continuously writes data and the parent drains in the signal handler.

Important APIs/types/functions: `stress_sigio_handler`, `stress_sigio`, `pipe`, `fcntl` with `F_SETOWN`, `F_GETFL`, `F_SETFL`, `O_ASYNC`, `O_NONBLOCK`, optional `F_SETPIPE_SZ`, `read`, `write`, `select`, `stress_affinity_change_cpu`, and OOM/scheduler helpers.

Control flow: the worker maps two 4 KiB buffers, creates a pipe, sets pipe size where possible, sets the read fd owner, forks a writer child, then the parent installs SIGIO and enables async nonblocking reads. The handler increments async signal count and drains the pipe until `EAGAIN`, timeout, or stop. The parent idles with `select` and checks any handler-recorded read error, then disables SIGIO, kills the child, restores fd flags, closes fds, and unmaps buffers.

State and persistence behavior: global volatile state holds the read fd, buffer pointer, async signal count, end time, error, and args pointer. All fd and mmap state is transient and cleaned up at exit.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify, and unimplemented without the required `fcntl` async flags. It integrates with CPU affinity, scheduler application, OOM adjustment, and stress-ng process state.

Risks and test signals: the handler performs non-async-signal-safe reads and bogo updates intentionally for stress coverage. Risks include missing SIGIO due to fd ownership quirks, EAGAIN/EINTR races, child write failures, and failure to restore file flags.
