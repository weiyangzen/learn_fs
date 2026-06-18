# sources/user-network-fs/samba/source4/lib/events/tevent_s4.c

## Purpose

`tevent_s4.c` implements Samba4's event-context initializer.

## Important APIs, Types, and Functions

It implements `s4_event_context_init()`, calling `samba_tevent_context_init()`, `samba_tevent_set_debug(ev, "s4_tevent")`, and `tevent_loop_allow_nesting(ev)`.

## Control Flow

The function allocates a tevent context under the supplied talloc parent. On success it sets Samba debug labeling and enables nested loops, then returns the context. On allocation failure it returns `NULL`.

## State and Persistence Behavior

The context lives under the caller's talloc parent. The helper mutates the context's debug and nesting settings but does not persist global state.

## Dependencies and Integration Points

It includes `includes.h`, defines `TEVENT_DEPRECATED`, includes `lib/events/events.h`, and is built into the private `events` library.

## Risks and Edge Cases

Nested loops can expose reentrancy problems in callers, but this is deliberate compatibility behavior. Callers must handle `NULL`.

## Test Signals

Signals include normal creation, allocation-failure handling, debug output under `s4_tevent`, and successful operation of services requiring nested event loops.
