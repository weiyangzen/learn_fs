# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_autoconf.c

## Scope

This file implements interrupt-driven autoconfiguration hooks: ordered callbacks that run after cold autoconfiguration when interrupts are available, plus registration and deregistration functions for device code.

## Public And Internal APIs Covered

- Public API: `config_intrhook_establish()`, `config_intrhook_disestablish()`.
- SYSINIT entry: `run_interrupt_driven_config_hooks()` at `SI_SUB_INT_CONFIG_HOOKS`.
- Internal state: hook list, `ran_config_hooks`, and `intr_config_lk`.

## Control Flow And Behavior

- Hooks are stored in an ordered tail queue of `struct intr_config_hook`.
- `run_interrupt_driven_config_hooks()` locks the list, marks a run generation, and repeatedly finds a hook whose `ich_ran` is zero.
- Each selected hook is marked ran, the lock is released, the callback executes, and the lock is reacquired. This lets callbacks disestablish themselves or allow other hook list changes.
- If all remaining hooks have already run but still remain on the list, the runner sleeps on the hook list and prints warnings every ten seconds.
- After thirty seconds, or on repeated runner invocation, it gives up with a warning that interrupt routing is likely broken.
- On real kernels, the first run waits up to five seconds after start to give USB/U4B configuration time before root mount probing.
- `config_intrhook_establish()` inserts a hook by `ich_order`, rejects duplicate registration, clears `ich_ran`, and if hooks already ran, invokes the runner immediately for late registration.
- `config_intrhook_disestablish()` removes a registered hook, wakes waiters, and panics if the hook was not registered.

## State And Data Structures

- `intr_config_hook_list` is protected by `intr_config_lk`.
- `ich_order` controls registration order; `ich_ran` prevents immediate repeated execution during a pass.
- `ich_desc`, `ich_func`, and `ich_arg` are used for diagnostics and callback invocation.

## Dependencies

- Depends on `lockmgr`, `lksleep`, `tsleep`, `wakeup`, global `ticks`/`hz`, and SYSINIT ordering.
- Used by drivers that need interrupts before completing device configuration.

## Risks And Invariants

- Hooks must disestablish themselves or be removed by their owners; otherwise boot can wait and warn.
- Callback execution occurs without the list lock, so hook storage must remain valid according to the hook owner's lifetime rules.
- Duplicate establish and unestablished disestablish are treated as programmer errors.
