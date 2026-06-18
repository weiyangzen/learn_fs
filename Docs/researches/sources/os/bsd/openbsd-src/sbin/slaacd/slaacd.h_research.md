# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/slaacd.h

Shared `slaacd` protocol and control header.

Constants:
- `_PATH_LOCKFILE`, `_PATH_SLAACD_SOCKET`, `SLAACD_USER`, `SLAACD_RTA_LABEL`.
- `SLAACD_SOIIKEY_LEN` and `MAX_RDNS_COUNT`.

Core types:
- `struct imsgev`: wraps `imsgbuf`, libevent event, handler, and event mask.
- `enum imsg_type`: daemon protocol covering control commands, socket passing, startup, interface updates/removals, RAs, address/route/RDNS proposals, and duplicate-address notifications.
- `enum rpref`: router preference low/medium/high.

Control payloads:
- Non-`SMALL` control structs expose interface info, RAs, RA prefixes, RA RDNS servers, address proposals, default-route proposals, and RDNS proposals.
- `struct imsg_propose_rdns`, `imsg_ifinfo`, `imsg_del_addr`, `imsg_del_route`, `imsg_ra`, and `imsg_dup_addr` define daemon-internal messages.

Declared helpers:
- `imsg_event_add()`, `imsg_compose_event()`, `imsg_forward_event()`.
- `sin6_to_str()` and `i2s()` in full builds; no-op string macros in `SMALL`.

Role:
- Central ABI-like header for the three-process `slaacd` architecture.
- Any changes here affect imsg compatibility across main, frontend, engine, and control code.
