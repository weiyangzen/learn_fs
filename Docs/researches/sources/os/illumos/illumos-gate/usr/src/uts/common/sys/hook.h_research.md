# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/hook.h

## Role

`hook.h` defines the exposed kernel hook framework types shared by hook providers and consumers.

## Key Interfaces and Data

- `HOOK_VERSION` is the current hook structure version.
- `hook_data_t` is an integer-sized event data payload.
- `hook_event_token_t` and `hook_token_t` are opaque handles to internal event and hook records.
- `hook_func_t` is the callback signature: event token, hook data, and caller argument.
- `hook_notify_cmd_t` enumerates notification actions: none, register, unregister.
- `hook_hint_t` controls insertion preference: none, first, last, before, or after.
- `hook_t` contains version, callback function, name, flags, insertion hint, hint value, and callback argument.
- `HOOK_INIT()` allocates and initializes a `hook_t`.
- `hook_family_t` names a family; `HOOK_FAMILY_INIT()` initializes it.
- `hook_event_t` names an event list, stores flags, and tracks whether callbacks are interested.
- `HOOK_RDONLY` marks read-only events where callbacks must not modify data and multiple callbacks are allowed.
- `HOOK_EVENT_INIT()` initializes event records.
- `hook_notify_fn_t` is the notification callback signature.
- Declares `hook_alloc()` and `hook_free()`.

## Dependencies and Use

The header includes queue and netstack types. Internal family/event storage is defined in `hook_impl.h`.

## Research Notes

This file deliberately exposes only allocation, initialization, and type definitions; registration and execution are internal framework functions in `hook_impl.h`.
