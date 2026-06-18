# sources/security-integrity/audit-userspace/src/auditd-reconfig.c

## Purpose
`auditd-reconfig.c` manages asynchronous configuration reload loading after SIGHUP. It isolates slow file parsing and DNS/name lookups from the main libev loop, then signals readiness back to `auditd.c`.

## Important APIs, Types, And Functions
Public APIs are `init_config_manager` and `start_config_manager`. Internals are `config_thread`, `config_lock`, and `config_thread_main`. It relies on external `reconfig_ready` and `send_audit_event`.

## Control Flow
`init_config_manager` initializes a mutex. `start_config_manager` attempts a nonblocking mutex lock; if no reload is active, it creates a detached thread with the incoming signal-info event; otherwise it logs failure, cleans the event, and returns an error. The thread blocks daemon signals, calls `load_config`, copies sender uid/pid/context from the original signal info into the new config, stores the config bytes inside the event's netlink buffer, sets `reply.conf`, changes the event type to `AUDIT_DAEMON_RECONFIG`, and calls `reconfig_ready`. On load failure it emits a failed config event, frees the temporary config, and cleans up.

## State And Persistence
The only persistent state is the reload mutex/thread handle. The new `daemon_conf` is transient until copied into the event buffer and later consumed by `auditd-reconfigure.c`.

## Dependencies And Integration
It depends on pthreads, signals, `libaudit`, `auditd-event.h`, `auditd-config.h`, and `private.h`. `auditd.c` starts it after receiving `AUDIT_SIGNAL_INFO` and later consumes readiness through a socketpair.

## Risks
Packing `struct daemon_conf` into `reply.msg.data` assumes the buffer can hold it and that pointer fields remain valid until the applier transfers/frees them. The mutex prevents concurrent reloads but rejected reloads become failed audit events. Ownership of `sender_ctx` and other strings crosses thread boundaries.

## Test Signals
No direct unit test exists. Tests should cover concurrent `start_config_manager`, load failure event emission, signal masking, event buffer layout, and cleanup when thread creation fails.
