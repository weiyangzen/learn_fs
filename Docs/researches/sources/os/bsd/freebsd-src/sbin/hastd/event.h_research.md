# File Research: sources/os/bsd/freebsd-src/sbin/hastd/event.h

`event.h` defines HAST worker-to-parent event IDs and declares the event API.

Key contents:
- Event constants from `EVENT_CONNECT` through `EVENT_SPLITBRAIN`.
- `EVENT_MIN` and `EVENT_MAX` validation bounds.
- Declares `event_send()` and `event_recv()`.

The event vocabulary matches hook names emitted by `event.c`.
