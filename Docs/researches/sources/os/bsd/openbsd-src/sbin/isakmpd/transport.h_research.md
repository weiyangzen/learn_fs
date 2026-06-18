# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/transport.h

This header defines isakmpd’s transport abstraction.

Key structures:
- `struct transport_vtbl`: transport method interface with create/reinit/remove/report, fd-set helpers, input handling, message sending, source/destination address accessors, ID decoding, cloning, and queue selection.
- `struct transport`: concrete or virtual transport instance with list link, vtable, normal and priority send queues, flags, reference count, and parent virtual transport pointer.
- `struct transport_list` and exported `transport_list`.

Flags:
- `TRANSPORT_LISTEN`: transport should be included in read fd sets.
- `TRANSPORT_MARK`: mark-and-sweep garbage collection marker.

Exported APIs:
- Transport creation, initialization, method registration, fd-set construction, message handling/sending, priority queue status, reporting, reinit, setup, reference, and release.

Integration:
- Used by UDP, UDP encapsulation, virtual transports, NAT-T, SA tracking, exchange/message retransmission, and the main event loop.
