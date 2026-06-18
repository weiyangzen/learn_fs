# sources/user-network-fs/samba/source3/lib/avahi.c

Purpose: adapts Avahi's `AvahiPoll` callback interface onto Samba's tevent loop.

Important APIs/types/functions: `struct avahi_poll_context`, private `AvahiWatch` and `AvahiTimeout` wrappers, `avahi_watch_new/update/get_events/free`, `avahi_timeout_new/update/free`, event handlers, and exported `tevent_avahi_poll()`.

Control flow: Avahi asks for fd watches or timers through the returned `AvahiPoll`. Watch creation appends a talloc-owned wrapper, registers a tevent fd handler, maps tevent read/write flags to Avahi flags, and invokes Avahi callbacks. Timeout creation optionally schedules a tevent timer; update frees the old timer and installs a new one or disables it.

State and persistence: all state is in-memory under the returned `AvahiPoll` talloc tree. Arrays of watches/timeouts are compacted with `memmove()` on free.

Dependencies/integration: uses `<avahi-common/watch.h>`, tevent fd/timer APIs, talloc, and Samba assertions. It is the bridge needed for mDNS/DNS-SD code to share Samba's event loop.

Risks/test signals: `AvahiWatch.fd` is never assigned in `avahi_watch_new()`, so callbacks may receive an uninitialized fd. `avahi_timeout_update()` asserts on timer allocation failure. Tests should register watches/timers, verify callback fd/event values, disable and reschedule timers, and free items from the middle of arrays.
