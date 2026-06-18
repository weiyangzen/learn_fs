# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/hook_impl.h

## Role

`hook_impl.h` defines internal data structures and function prototypes for the kernel hook framework implementation.

## Key Interfaces and Data

- `fwflag_t` and related masks coordinate add/delete/destroy operations and wait states.
- `flagwait_t` combines a condition variable, mutex, flags, and owner wait lock.
- The comments diagram the hierarchy: hook stacks contain families; families contain events; events contain registered hooks and notification callbacks.
- `hook_hook_kstat_t` stores per-hook kstats: version, flags, hint, hint value, position, and hit count.
- `hook_int_t` wraps public `hook_t` with queue linkage, kstats, kstat pointer/name, and notify lock.
- Tail queues hold hook and notification records.
- `hook_notify_t` stores notify callback, argument, and flags.
- `hook_event_kstat_t` stores hooks-added, hooks-removed, and event count.
- `hook_event_int_t` wraps a public event with locks, event list linkage, hook list, kstats, notification list, waiter, and condemned/shutdown flags.
- `hook_family_int_t` wraps a family with locks, event list, kstat, owning stack, notification list, waiter, and lifecycle flags.
- `hook_stack_t` stores per-netstack hook families, netstack pointer/ID, notifications, shutdown state, and waiter.
- Defines standard family names `Hn_ARP`, `Hn_IPV4`, `Hn_IPV6`, and `Hn_VIONA`.
- Declares internal operations for running hooks, registering/unregistering hooks, event add/remove/shutdown, family add/remove/shutdown, and stack notifications.

## Dependencies and Use

The header includes public hook definitions, condition-variable internals, and netstack types. It is implementation-private and not intended for hook consumers.

## Research Notes

Lifecycle coordination is explicit: add/delete/destroy operations can block each other through flag/wait masks, preventing unsafe mutation of event and family lists while callbacks or notifications run.
