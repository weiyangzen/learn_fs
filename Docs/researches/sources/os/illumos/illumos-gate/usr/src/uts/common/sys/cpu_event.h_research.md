# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpu_event.h

## Role

Defines kernel CPU idle event notification and per-CPU idle property APIs.

## Idle Callback Priorities

- Priority classes:
  - High static priorities.
  - Dynamic priorities.
  - Low static priorities.
- Constants include `CPU_IDLE_CB_PRIO_LOW_BASE`, `CPU_IDLE_CB_PRIO_DYN_BASE`, `CPU_IDLE_CB_PRIO_HIGH_BASE`, and reserved base.
- `CPU_IDLE_CB_PRIO_DYNAMIC` asks the framework to assign ordering.
- Fixed callback priorities exist for DTrace and, on x86, TLB flushing.

## Idle Properties

Property names include:

- `idle-state`
- `enter-ts`
- `exit-ts`
- `last-idle-time`
- `last-busy-time`
- `total-idle-time`
- `total-busy-time`
- `interupt-count` spelling as present in source

Property types are represented by `cpu_idle_prop_type_t`, and values use `cpu_idle_prop_value_t`.

## Callback API

- `cpu_idle_enter_cbfn_t`: called before hardware idle entry, in idle thread context, interrupts disabled.
- `cpu_idle_exit_cbfn_t`: called on idle exit, in idle thread or interrupt context, interrupts disabled.
- `cpu_idle_check_wakeup_t`: lets callbacks check and report already-pending wakeups.
- `cpu_idle_callback_t`: versioned callback pair.
- `cpu_idle_register_callback()` / `cpu_idle_unregister_callback()` manage callbacks.

## Idle State API

- `cpu_idle_enter()`: notifies entry; returns non-zero if hardware idle should be canceled.
- `cpu_idle_exit()`: notifies exit.
- `cpu_idle_get_context()`: returns current CPU context.
- `cpu_idle_get_cpu_state()`: fetches CPU idle state.

## Property API

Supports creating/destroying properties and handles, querying type/name, getting values in typed forms, setting a current-CPU value, and setting all CPUs.

## Lifecycle

- `cpu_event_init()`
- `cpu_event_init_cpu(cpu_t *)`
- `cpu_event_fini_cpu(cpu_t *)`

## Research Relevance

Important for CPU power, idle accounting, DTrace, and platform wakeup coordination. Filesystem relevance is indirect through scheduling, power transitions, and timing behavior during I/O idle periods.
