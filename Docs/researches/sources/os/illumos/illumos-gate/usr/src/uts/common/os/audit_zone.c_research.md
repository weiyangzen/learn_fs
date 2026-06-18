# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/audit_zone.c

This file manages per-zone audit kernel contexts through a zone key. Each zone receives an `au_kcontext_t` with audit identity, policy, queue configuration, statistics, service locks, condition variables, and door-buffer storage.

`au_zone_init()` allocates and initializes a context. For zone 0 it records the global context and attaches it to `global_zone`; for non-global zones it inherits policy from the global context and attaches the context to the current process zone. It sets validity, zone id, default IPv4 terminal id, `AU_NOAUDITID`, initial audit state, queue high/low watermarks, buffer sizes, delay, statistics version/event count, door buffer, and all queue/service locks and condition variables.

`au_zone_shutdown()` sends a shutdown door message when auditing is loaded and the context has an active audit output target, marks the context invalid, forces audit state to no-audit, wakes the output thread, and destroys the per-zone taskq if output was active. `au_zone_destroy()` asserts no-audit state, destroys locks and condition variables, frees any queued audit record, releases the door buffer, and frees the context. `au_zone_setup()` registers these callbacks with `zone_key_create()`, and `au_zone_getstate()` returns either the supplied context state or the current zone context state.

Key dependencies are zone lifecycle callbacks, audit queues and records, audit door messaging, taskqs, and global audit policy/state. Correctness depends on orderly shutdown of active output before destroying queue state and on inheriting global policy for zones created after the global audit context exists.
