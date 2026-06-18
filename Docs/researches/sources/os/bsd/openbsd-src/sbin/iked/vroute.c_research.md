# File Research: sources/os/bsd/openbsd-src/sbin/iked/vroute.c

This file implements OpenIKED virtual route, DNS, and interface-address management. It lets less-privileged OpenIKED processes request network configuration changes via imsg, while the parent performs routing socket and ioctl operations.

Key responsibilities:
- Initializes route/ioctl sockets and cleanup tracking state in `vroute_init`.
- Reads routing socket messages in `vroute_rtmsg_cb`, especially DNS proposal solicitations, and re-advertises tracked DNS proposals.
- Tracks added interface addresses, routes, and DNS proposals in TAILQs so `vroute_cleanup` can remove them on shutdown.
- Serializes child-to-parent requests:
  - `vroute_setaddr` / `vroute_getaddr`
  - `vroute_setdns` / `vroute_getdns`
  - `vroute_setaddroute`, `vroute_setcloneroute`, `vroute_setdelroute`, `vroute_setroute`
  - `vroute_getroute`, `vroute_getcloneroute`
- Maintains cleanup lists with insert/remove helpers for routes, DNS, and addresses.
- Emits DNS proposals with `vroute_dodns`.
- Emits route messages over `AF_ROUTE` with `vroute_doroute`, including route GET handling.
- Parses route GET replies in `vroute_process`.
- Applies interface addresses with `vroute_doaddr` using `SIOCAIFADDR`/`SIOCDIFADDR` for IPv4 and `SIOCAIFADDR_IN6`/`SIOCDIFADDR_IN6` for IPv6.

Important OS interactions:
- `socket(AF_ROUTE, SOCK_RAW, AF_UNSPEC)`
- `setsockopt(AF_ROUTE, ROUTE_MSGFILTER, ...)`
- routing messages `RTM_ADD`, `RTM_DELETE`, `RTM_GET`, and `RTM_PROPOSAL`
- interface address ioctls on IPv4/IPv6 datagram sockets

Security and correctness notes:
- The design centralizes privileged network mutations in the parent process.
- Imsg parsing performs length checks before reading variable-length sockaddr payloads.
- Added state is recorded before OS operations for cleanup coordination.
- Notable implementation quirk: `vroute_setaddr` zeroes the `mask` integer parameter before computing IPv4 masks, which makes the fallback full-length mask path always used for IPv4 in that function. This should be checked against upstream intent.
