# File Research: sources/os/plan9/9front/sys/src/9/xen/devxenstore.c

Xenstore device and kernel RPC helper.

Purpose:
- Implements Plan 9 `#x` device for Xenstore control and watch access.
- Provides kernel helpers for reading/writing xenstore nodes.

Key behavior:
- Maps Xenstore shared ring at `XENBUS` and uses Xen event channel from `start_info`.
- `xwrite` and `xread` move request/response bytes through Xenstore ring indices with wraparound handling.
- `xsrpc` serializes requests, assigns request IDs, matches out-of-order responses, handles watch events, and queues response payloads.
- Exposes `#x/xenstore` and `#x/xenwatch`.
- `xscmd`, `xenstore_read`, `xenstore_write`, `xenstore_setd`, and `xenstore_gets` provide in-kernel synchronous commands.
- `xenbusproc` watches `control/shutdown` and translates Xen poweroff/reboot requests into `reboot`/`exit`.

Integration:
- Required by Xen block/network frontend discovery, backend negotiation, console and shutdown handling.

Risks/notes:
- A comment flags a possible buffer overflow in `xscmd` when reading payloads into a fixed local buffer.
- Request matching logic is subtle because watch responses can arrive without a normal requester.
