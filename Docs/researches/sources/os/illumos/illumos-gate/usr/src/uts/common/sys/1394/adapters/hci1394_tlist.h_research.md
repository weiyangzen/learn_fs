# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_tlist.h

This private header defines a timed doubly linked list used by `hci1394`.

Main types:
- `hci1394_tlist_node_t`: embeddable node with public `tln_addr` and private on-list, expiry time, prev, and next fields.
- `hci1394_tlist_callback_t`: callback invoked for expired nodes.
- `hci1394_tlist_timer_t`: timeout interval, timer resolution, callback, and callback arg.
- `hci1394_tlist_timeout_state_t`: timeout off/on state.
- `hci1394_tlist_t`: list head/tail, timer enabled flag, timeout state/id, timer config copy, driver info, and mutex.

APIs:
- Init/fini.
- Add, delete, get head, peek head.
- Update timeout and cancel timeout.

Behavior:
- Nodes are added to tail and can be atomically deleted from any position.
- Optional timeout removes nodes older than the configured timeout and invokes the callback.
- The timer is only active while the list contains entries.
