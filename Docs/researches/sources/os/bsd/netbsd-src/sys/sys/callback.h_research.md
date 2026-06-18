# File Research: sources/os/bsd/netbsd-src/sys/sys/callback.h

## Scope

Declares a small callback chain framework.

## APIs And Data Structures

- `callback_entry` stores TAILQ linkage, callback function pointer, and object pointer.
- `callback_head` stores mutex, condition variable, callback queue, next entry pointer, entry count, running count, and flags.
- Callback functions return `CALLBACK_CHAIN_CONTINUE` or `CALLBACK_CHAIN_ABORT`.
- Declares run, register, unregister, init, and destroy operations.

## Dependencies

- Includes queue, mutex, and condition variable headers.

## Risks And Invariants

- The head tracks current iteration with `ch_next` and `ch_running`, so unregister must coordinate with active callbacks.
- Callback return values control whether a round-robin run continues.
