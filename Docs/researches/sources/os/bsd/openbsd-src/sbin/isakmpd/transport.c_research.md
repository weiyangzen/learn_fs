# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/transport.c

This file implements common transport registration, reference counting, select-loop integration, send queues, and retransmission scheduling.

Key APIs:
- `transport_init()`: initializes global transport instance and method lists.
- `transport_method_add()`: registers a transport vtable such as UDP or UDP encapsulation.
- `transport_setup()`: initializes top-level virtual transports or inserts concrete transports into the global list.
- `transport_reference()` / `transport_release()`: manage transport lifetimes and call method `remove` on final release.
- `transport_reinit()`: calls registered method reinitializers.
- `transport_fd_set()` and `transport_pending_wfd_set()`: build read/write fd sets for listening transports and queued outbound messages.
- `transport_handle_messages()`: dispatches readable transports to virtual transport message handlers.
- `transport_send_messages()`: sends queued messages, schedules retransmissions, runs post-send hooks, and frees messages no longer needed.
- `transport_prio_sendqs_empty()`, `transport_report()`, `transport_create()`.

Behavior and integration:
- Maintains `transport_list` for concrete transports and `transport_method_list` for registered methods.
- Virtual transports own normal and priority send queues; priority queue is used for important messages such as DELETE notifications.
- Retransmission delay is simple linear/backoff-like `msg->xmits * 2 + 5`; limit comes from `General/retransmits`, default 10.
- Uses `message_send_expire`, `message_post_send`, `message_free`, and exchange `last_sent`/`in_transit` state to coordinate retransmissions.

Risk notes:
- Multiple transports may share a socket; `transport_send_messages()` clears the fd bit after one send, so earlier list entries can be favored.
- Transport references are raised before send-loop iteration so virtual transports are not removed while being used.
- The retransmission logic is explicitly called delicate in comments and is tied to exchange lifetime semantics.
