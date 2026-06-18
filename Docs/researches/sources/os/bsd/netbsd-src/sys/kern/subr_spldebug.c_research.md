# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_spldebug.c

Read completely: 122 lines.

This is a small interrupt-priority-level debugging aid. It records where code raises to `IPL_HIGH` and notes the most recent lower operation per CPU when debugging is enabled.

State:
- `spldebug` gates all tracing.
- `splraise_retaddrs[MAXCPUS][32][4]` stores up to 32 raise events per CPU, each with up to four return addresses.
- `splraise_depth`, `spllowered_to`, and `spllowered_from` track per-CPU state.

Functions:
- `spldebug_start` and `spldebug_stop` toggle tracing.
- `spldebug_lower` resets the per-CPU raise stack and records the lowered IPL, ignoring `IPL_HIGH`.
- `spldebug_raise` records a call stack when raising to `IPL_HIGH`, using `return_address(i)`.

Integration: this depends on MD return-address support and CPU indexing. It is diagnostic state only; there is no synchronization beyond per-current-CPU access assumptions.

Reliability notes: once a CPU reaches the fixed stack length, new raise records are ignored. The `spllowered_from` return-address capture is disabled under `#if 0`, so only the lowered IPL is currently retained.
