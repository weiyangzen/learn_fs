# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/session.c

## Purpose

Manages process sessions and controlling terminal lifecycle: session reference counts, session creation, safe controlling-tty lookup, ctty assignment, ctty release, SIGHUP delivery, and compatibility `vhangup()` behavior.

## Key State

- `session0` is the primordial session.
- Each `sess_t` tracks session ID pid pointer, lock, reference count, ctty hold count, exit-in-progress flag, SIGHUP flag, controlling tty device/vnode, and credential.
- `s_cnt` protects active `tty_hold()` users while `s_ref` protects session structure lifetime.

## Key Interfaces

- `sess_hold()` and `sess_rele()` manage session references. `sess_rele()` frees non-`session0` sessions only when no process can acquire a new reference.
- `tty_hold()` obtains a stable current session and ctty-related hold, waiting if the session leader is exiting and clearing the ctty.
- `tty_rele()` releases a ctty hold and session reference.
- `sess_create()` creates a new session for `curproc`, updates process group/session links, and releases the old session.
- `strctty()` makes a stream the controlling tty for a session leader after validating stream/session state and waiting for outstanding tty holds.
- `freectty()` releases the current session leader's controlling tty, sends SIGHUP/stream hangup once, waits for outstanding holds, clears bindings, closes/releases vnode and credentials, and releases pid holds.
- `vhangup()` only performs privilege check and returns success; comments state the historical behavior effectively did nothing.
- `cttydev()` returns a process's controlling tty device.
- `ctty_clear_sighuped()` clears the session SIGHUP marker.

## Internal Helpers

- `sess_ctty_set()` establishes ctty vnode, credential, stream session ID, and foreground process group, taking pid and credential holds.
- `sess_ctty_clear()` clears session and stream ctty bindings without freeing referenced objects.
- `freectty_lock()` acquires `sd_lock`, `pidlock`, `p_splock`, and `s_lock` in a safe order, using temporary holds when not exiting.
- `freectty_signal()` sends SIGHUP to the foreground group and calls `strhup()` while managing lock dropping and holds.

## Locking

- Locking is explicit and central: `sd_lock`, `pidlock`, `p_splock`, `s_lock`, `p_lock`, and credential locks all appear.
- The code repeatedly drops and reacquires locks to respect stream/proc/session lock ordering, using `s_ref` and `s_cnt` to keep objects stable.
- At process exit, `freectty()` uses noninterruptible waits because ctty cleanup must complete.

## Dependencies

Depends on process/session/pid structures, STREAMS `stdata_t`, vnode close/release operations, credentials, signal delivery, stream hangup, and security policy for `vhangup()`.

## Notes for Future Work

- The comments highlight intentionally complex lock ordering; changes must preserve the temporary hold patterns around lock drops.
- `freectty()` returns `EIO` when there is no releasable ctty and `1` on successful release, which is unusual but established here.
