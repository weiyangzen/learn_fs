# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockfilter_impl.h

## Purpose
Internal header for the sockfs socket filter framework.

## Main Behavior
- Defines `sof_module_t`, `sof_entry_t`, `sof_instance_t`, and filter/global kstat structures.
- Sets filter constants such as maximum name length, max socket tuple count, and module path.
- Defines entry flags for automatic, programmatic, and condemned filters.
- Defines instance flags for bypass, deferred accept, receive flow control, and send flow control.
- Declares filter entry, sockparams, sonode attach/cleanup/notify, option, dispatch, and data filtering functions.
- Defines `SOF_INTERESTED()` and `__SOF_FILTER_OP()` macros for checking callbacks and walking the filter stack.
- Provides convenience macros for outbound data filtering.

## Integration Points
- Included by `sockfilter.c`, `sockcommon_sops.c`, `sockcommon_subr.c`, `socknotify.c`, and `sockparams.c`.
- Depends on public filter APIs from `sys/sockfilter.h`.

## Risks and Notes
- `__SOF_FILTER_OP()` returns immediately when a filter does anything other than `SOF_RVAL_CONTINUE`, so callback ordering directly controls behavior.
- The misspelled flag name `SOFEF_CONDEMED` is part of the internal ABI within this source set.
- Instance list direction matters: many operations traverse top-down, while inbound data and notifications often traverse bottom-up.
