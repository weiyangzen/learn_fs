# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/ub_event_pluggable.c

Implements the pluggable event abstraction declared in `ub_event.h`.

Backend wrapping:
- Defines private `struct my_event_base` containing `struct ub_event_base` plus native `struct event_base*`.
- Defines private `struct my_event` containing `struct ub_event` plus native `struct event`.
- Uses vtables from `libunbound/unbound-event.h`; public functions validate `UB_EVENT_MAGIC` and dispatch through the vtable.
- Default vtables wrap libevent/libev/mini-event operations.

Event-bit handling:
- If Unbound event bits differ from native backend bits, macros translate between them.
- Callback wrapper functions are generated for known internal callbacks so native events can call back with translated bit values.
- `NATIVE_BITS_CB` maps known callback addresses to wrappers; unknown callbacks become NULL in that translation mode.

Base creation:
- `ub_default_event_base` creates a mini-event base when `USE_MINI_EVENT` is set.
- Otherwise it creates libev or libevent bases depending on configured APIs.
- `ub_libevent_event_base` wraps an externally supplied libevent base when not using mini-event.
- `ub_libevent_get_event_base` exposes the native base only for the default wrapper vtable and non-mini-event builds.

Event creation and operations:
- `my_event_new` uses `event_set` and `event_base_set`.
- `my_signal_new` uses `signal_set`.
- Timer add reinitializes the event as timeout-only and uses `evtimer_add`.
- Add/delete/free/set-fd/bit operations manipulate the underlying `struct event`.
- Winsock registration only works for `USE_MINI_EVENT && USE_WINSOCK`; otherwise those helpers are no-ops or return NULL.

System reporting:
- `ub_get_event_sys` reports backend name/system/method for Winsock, mini-event, libev, or libevent.
- libev backend method can be mapped to strings like select, poll, epoll, kqueue, devpoll, or evport when backend constants are available.

Time update:
- `ub_comm_base_now` updates the `comm_base` cached `time_t` and `timeval` using `gettimeofday`, except when mini-event owns time updates.

Safety/integration:
- Public wrappers check magic values and use `fptr_wlist` assertions to ensure default vtable entries match expected local functions.
- This file is central glue between Unbound networking code, libunbound pluggable event users, and platform-specific event backends.
