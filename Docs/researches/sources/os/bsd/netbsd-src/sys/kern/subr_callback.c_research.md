# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_callback.c

## Summary
Implements a small round-robin callback chain abstraction with registration, unregistration, and serialized run tracking.

## Main Responsibilities
- Initializes and destroys `struct callback_head` lock, condition variable, queue, and counters.
- Registers callback entries with function/object pairs.
- Unregisters callbacks after waiting for active runs to finish.
- Runs one round over the current entries, stopping when a callback returns something other than `CALLBACK_CHAIN_CONTINUE`.

## Important Behavior
`callback_run_roundrobin()` snapshots `ch_nentries` after marking the chain running, then invokes at most that many callbacks. `ch_next` preserves round-robin position between runs and is adjusted if an unregister removes the next entry.

## Dependencies
Uses `TAILQ`, mutexes, condition variables, and callback structures from `sys/callback.h`.

## Risks
Callbacks run without holding `ch_lock`; unregistration waits for `ch_running` to drop to zero. Callers must ensure callback entries remain valid until `callback_unregister()` returns.
