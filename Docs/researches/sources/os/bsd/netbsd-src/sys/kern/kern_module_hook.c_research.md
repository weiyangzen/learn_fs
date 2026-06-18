# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_module_hook.c

## Purpose
Provides synchronization primitives for optional module hooks so callers can enter hook code locklessly on the hot path while module load/unload safely publishes or withdraws hook availability.

## Main Interfaces
- `module_hook_init`: initializes mutex, condition variable, and pserialize domain.
- `module_hook_set(hooked, lc)`: initializes a localcount, performs a global pserialize barrier, then publishes `*hooked = true`.
- `module_hook_unset(hooked, lc)`: clears `hooked`, performs pserialize to block new entrants, drains existing localcount users, and finalizes the localcount.
- `module_hook_tryenter(hooked, lc)`: pserialize read section that checks hook availability and acquires localcount if enabled.
- `module_hook_exit(lc)`: releases localcount and wakes drain waiters.

## Internal State And Dependencies
- Static `module_hook` object holds `kmutex_t`, `kcondvar_t`, and `pserialize_t`.
- Requires `kernconfig_is_held()` for set/unset.
- Uses relaxed atomic loads/stores paired with pserialize barriers and localcount drain.

## Control Flow Notes
- Set path performs setup before publishing the hook.
- Unset path prevents new entrants, waits for all CPUs to leave pserialize readers, then waits for active hook calls to release localcount.
- Callers use `tryenter`/`exit` around hook invocation.

## Risk Areas
- Correctness depends on every hook caller pairing successful `tryenter` with `module_hook_exit`.
- The design intentionally uses heavy pserialize operations only during load/unload, not during hook calls.
- `hooked` and `localcount` storage are owned by the hook user; this file only coordinates access.

## Filesystem Relevance
Indirect. Useful for optional kernel module hooks, potentially including VFS or filesystem module integration points.
