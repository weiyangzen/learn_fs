# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_thread.c

Small thread lifecycle abstraction used by the SMB server. It wraps kernel thread creation, cooperative stop signaling, and wait/continue helpers around `smb_thread_t`.

`smb_thread_init` zeroes and initializes a thread object with name, entry point, argument, priority, server pointer, mutex, condition variable, and magic/state values. `smb_thread_destroy` asserts the object is exited and tears down synchronization primitives.

`smb_thread_start` transitions from `EXITED` to `STARTING`, creates either an LWP-backed kernel thread for priorities below `MINCLSYSPRI` or a regular kernel thread, records the thread pointer and dispatch ID, then waits for the new thread to reach `RUNNING` or fail. The common `smb_thread_entry_point` sets `RUNNING`, invokes the real entry point unless killed early, then clears the thread pointer, marks `EXITING`, broadcasts, and exits via `lwp_exit` when needed or `thread_exit`.

`smb_thread_stop` is cooperative. It sets `sth_kill`, broadcasts, waits for `EXITING`, joins by dispatch ID, then marks `EXITED` and clears kill state. It also handles already exiting or already exited states. `smb_thread_signal` wakes a running thread.

`smb_thread_continue`, `smb_thread_continue_nowait`, and `smb_thread_continue_timedwait` provide the canonical loop condition for worker functions. The locked helper interprets ticks `0` as indefinite wait, `-1` as nonblocking check, otherwise relative timed wait, and returns false once `sth_kill` is set.
