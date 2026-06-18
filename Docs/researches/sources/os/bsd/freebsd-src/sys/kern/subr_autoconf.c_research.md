# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_autoconf.c

## Summary
Implements interrupt-driven autoconfiguration hooks. Drivers can register callbacks that run once cold autoconfiguration has completed and interrupts are usable, and boot waits until all registered hooks are disestablished.

## Main Responsibilities
- Maintains a global STAILQ of `intr_config_hook` entries.
- Runs hooks in registration order while allowing hooks registered during a run to be picked up.
- Provides one-shot hook allocation and automatic disestablishment.
- Blocks boot progress until the hook list is empty.
- Provides drain semantics for callers that need to cancel or wait for a hook.
- Offers a DDB show command for pending hooks when DDB is enabled.

## Key APIs
- `config_intrhook_establish()`: registers a hook and queues it for notification.
- `config_intrhook_oneshot()`: allocates a wrapper hook that unregisters itself after running.
- `config_intrhook_disestablish()`: removes a registered hook and wakes waiters.
- `config_intrhook_drain()`: returns whether a hook was done, queued and removed, or running and waited for.
- `boot_run_interrupt_driven_config_hooks()`: SYSINIT boot wait path.

## Important Behavior
`run_interrupt_driven_config_hooks()` is reentrancy-safe through a static `running` flag. If hook execution is already active, a later caller returns and lets the active runner process newly registered hooks via `next_to_notify`.

Boot-time waiting emits a diagnostic every 60 seconds for up to six intervals, using linker symbol lookup when possible to print hook names, then asserts if waiting too long.

When `cold == 0`, establishing a hook immediately runs the interrupt-driven hook processor, with comments noting that a task-based dispatch might be more appropriate for some driver reentrancy expectations.

## State and Synchronization
The hook list, `next_to_notify`, and hook states are protected by `intr_config_hook_lock`. The wait path sleeps on the list head and wakes whenever a hook is disestablished. TSLOG hold/release/wait calls annotate boot blocking.

## Dependencies
Uses STAILQ, mutexes, msleep/wakeup, kernel malloc/free for one-shot hooks, linker symbol lookup, SYSINIT, and optional DDB.

## Risks
Hooks are expected to disestablish themselves or be disestablished by their driver; otherwise boot blocks indefinitely until the warning assertion fires. `config_intrhook_drain()` waits for running hooks by polling with timed sleeps.
