# sources/user-network-fs/samba/source3/include/util_event.h

## Purpose
`util_event.h` declares a source3 tevent helper for recurring idle callbacks.

## Important APIs, Types, and Functions
- Opaque `struct idle_event`.
- `event_add_idle(struct tevent_context *event_ctx, TALLOC_CTX *mem_ctx, struct timeval interval, const char *name, bool (*handler)(const struct timeval *now, void *private_data), void *private_data)`.

## Control Flow and State
The helper registers an idle event in a tevent loop. The handler receives the current time and private data and returns a boolean that likely controls whether the idle event remains scheduled. Event state is owned by the returned `idle_event` and its talloc context.

## Persistence Behavior
No persistent storage. The helper maintains in-memory event-loop state until freed or cancelled.

## Dependencies and Integration Points
It includes `replace.h` and `tevent.h` and is implemented in `lib/util_event.c`. It integrates with long-running source3 daemons that need periodic idle work without blocking request handling.

## Risks
- Handler runtime must be short; blocking idle handlers can delay the event loop.
- Ownership of `private_data` and the returned event must be clear to avoid use-after-free.
- Time interval handling must be robust against clock changes if wall-clock time is used downstream.

## Test Signals
tevent loop tests for repeated execution, handler false/cleanup behavior, talloc ownership cleanup, and daemon idle-maintenance tests are relevant.
