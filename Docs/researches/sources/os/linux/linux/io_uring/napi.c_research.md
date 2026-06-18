# File Research: sources/os/linux/linux/io_uring/napi.c

NAPI busy-poll integration for io_uring, compiled under `CONFIG_NET_RX_BUSY_POLL`.

Key flows:
- Context init/free initializes NAPI list/hash state, spinlock, busy-poll timeout, preferred busy-poll mode, and tracking mode.
- Dynamic tracking adds socket `sk_napi_id` values through `__io_napi_add_id()` and expires stale entries after `NAPI_TIMEOUT`.
- Static tracking allows explicit add/delete via registration commands.
- Busy-loop execution iterates registered NAPI IDs under RCU and calls `napi_busy_loop_rcu()` until signal, completion, local work, or timeout.
- `io_register_napi()` copies current settings back to userspace, validates requested opcode/settings, and configures tracking.
- `io_unregister_napi()` reports current settings if requested, disables tracking, clears timeout/preference, and frees entries.
- SQPOLL busy-poll path runs a nonblocking busy loop if configured and entries exist.

Important details:
- Busy-poll timeout is capped to 10 ms on registration.
- IOPOLL rings reject NAPI registration.
- Dynamic add uses spinlock plus tracking-mode recheck to avoid races with registration mode changes.
