# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fx.h

## Role

`fx.h` defines kernel data structures for the fixed-priority scheduling class and a private callback interface for partner/custom scheduler integration.

## Key Interfaces and Data

- `fxdpent_t` is a dispatch table entry: global priority and time quantum.
- Kernel-only `fx_cookie_t` identifies callback-supplied storage.
- `fx_callbacks_t` lets external scheduler logic observe or alter scheduling on exit, tick, preempt, stop, sleep, and wakeup.
- Callback versioning uses `FX_CALLB_VERSION_1` and `FX_CALLB_REV`.
- `FX_CB_*` macros invoke callback members directly.
- `FX_CB_NOCHANGE` is the priority/quantum no-change sentinel.
- `fxproc_t` is per-thread fixed-priority class state: quantum, remaining time, priority, user priority limit, nice value, flags, owning thread, callback linkage, callback cookie, and CPU caps data.
- `FXBACKQ` indicates a thread should return to the back of the dispatch queue after preemption.
- `fxkparms_t` is the kernel version of fixed-priority parameters.
- Private kernel functions include `fx_register_callbacks()`, `fx_unregister_callbacks()`, `fx_modify_priority()`, `fx_get_mutex_cookie()`, and `fx_get_maxpri()`.

## Dependencies and Use

The header includes scheduler, thread, DDI, and CPU capability types. Public dispatch table definitions are visible broadly; callback and process structures are `_KERNEL` only.

## Research Notes

The callback contract is a sensitive scheduling extension point: callbacks can change priority and quantum immediately by modifying out-parameters.
