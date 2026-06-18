# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/session.h

## Role

Defines kernel session state, controlling terminal references, locking rules, and session-management entry points.

## Key Interfaces

- `sess_t` stores immutable session ID pointer plus lock-protected reference count, controlling TTY state, exit state, active TTY users, device, vnode, and credentials.
- `s_sid` aliases `s_sidp->pid_id`.
- Exports kernel `session0`.
- Kernel functions include session reference handling, controlling TTY hold/release, session creation, STREAMS controlling-TTY setup, freeing controlling TTY, querying controlling TTY device, and clearing SIGHUP state.

## Locking Contract

The header documents lock order as `sd_lock -> pidlock -> p_splock -> s_lock`. `pidlock` or `p_splock` protects `proc_t::p_sessp`; `s_lock` protects session contents. `tty_hold()` prevents controlling TTY changes by incrementing `s_cnt`.

## Risk Notes

Session and controlling-terminal logic is lock-order sensitive. Direct mutation outside session management code risks races with process session changes and terminal hangup behavior.
