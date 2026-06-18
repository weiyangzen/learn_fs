# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/ub_event.h

Declares Unbound’s event abstraction layer.

Key concepts:
- Opaque `struct ub_event_base` and `struct ub_event`.
- Event bit constants mirror libevent/libev concepts: timeout, read, write, signal, persist.
- The API hides whether the backend is mini-event, libevent, libev, or Winsock.

Public API:
- Version/system info: `ub_event_get_version`, `ub_get_event_sys`.
- Base management: `ub_default_event_base`, `ub_libevent_event_base`, `ub_libevent_get_event_base`, `ub_event_base_free`, `ub_event_base_dispatch`, `ub_event_base_loopexit`.
- Event creation: `ub_event_new`, `ub_signal_new`, `ub_winsock_register_wsaevent`.
- Event mutation/lifetime: `ub_event_add_bits`, `ub_event_del_bits`, `ub_event_set_fd`, `ub_event_free`, `ub_event_add`, `ub_event_del`.
- Specialized activation: `ub_timer_add`, `ub_timer_del`, `ub_signal_add`, `ub_signal_del`.
- Winsock helpers: `ub_winsock_unregister_wsaevent`, `ub_winsock_tcp_wouldblock`.
- Time helper: `ub_comm_base_now`.

Usage role:
- This is the interface consumed by networking and tube code so they do not directly depend on a specific event backend.
