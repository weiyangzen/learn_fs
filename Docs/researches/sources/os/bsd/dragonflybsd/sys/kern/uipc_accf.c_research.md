# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_accf.c

## Summary
Accept-filter registry for sockets. It lets modules add, find, and logically remove named accept filters.

## Main Responsibilities
- Maintains global `accept_filtlsthd`.
- Exposes `accept_filt_add`, `accept_filt_del`, and `accept_filt_get`.
- Provides `accept_filt_generic_mod_event` for module load/unload/shutdown.
- Exposes `net.inet.accf.unloadable` sysctl.

## Important Behavior
Loaded filters are copied into `M_ACCF` memory. Deletion sets `accf_callback` to NULL rather than removing/freeing the registry entry, intentionally leaking/reusing the structure to avoid dangling callbacks after module unload.

By default unload is refused with `EOPNOTSUPP`; setting `unloadable` permits callback nulling but the comments call this unsafe without refcounts.

## Risks
No accept-filter reference counting exists here. Enabling unload can leave sockets with stale callback assumptions unless the rest of the stack guarantees no active users.
