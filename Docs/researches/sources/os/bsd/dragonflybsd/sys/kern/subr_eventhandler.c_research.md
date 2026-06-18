# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_eventhandler.c

## Summary
Provides the kernel eventhandler registry: named lists of callback entries sorted by priority, protected by a global LWKT token.

## Main Responsibilities
- Defines `M_EVENTHANDLER` allocation type and the global `eventhandler_lists`.
- `eventhandler_register()` finds or lazily creates a named list, initializes entries, and inserts the callback by priority.
- `eventhandler_deregister()` removes one handler or clears an entire list.
- `eventhandler_find_list()` locates a named eventhandler list.

## Important Behavior
Registration is MPSAFE under `evlist_token`. Priority insertion is O(n), but equal-priority append is effectively O(1). Dynamically created list names are stored immediately after the allocated `eventhandler_list` structure.

## Risks
Deregistering an entire list frees entries but does not remove the list structure itself. Callers must pass the correct list/tag pairing; the file notes a missing diagnostic check.
