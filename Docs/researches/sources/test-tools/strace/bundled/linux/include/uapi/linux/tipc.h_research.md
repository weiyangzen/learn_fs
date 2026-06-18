# sources/test-tools/strace/bundled/linux/include/uapi/linux/tipc.h

## Purpose

Defines the TIPC socket ABI: addressing primitives, service subscriptions, socket address layout, options, ioctl payloads, AEAD key handling, and deprecated address helpers. strace uses it to decode `AF_TIPC` socket addresses, options, ancillary data, and ioctls.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h` and `linux/sockios.h`. It exports `tipc_socket_addr`, `tipc_service_addr`, `tipc_service_range`, service type constants, `enum tipc_scope`, message size/importance/rejection constants, subscription filter bits, `struct tipc_subscr`, `tipc_event`, `sockaddr_tipc`, ancillary data names, socket options from `TIPC_IMPORTANCE` through `TIPC_NODELAY`, group flags and `tipc_group_req`, bearer name length constants, `SIOCGETLINKNAME`, `SIOCGETNODEID`, request structs, `tipc_aead_key`, key length macros, `tipc_aead_key_size`, `TIPC_REKEYING_NOW`, deprecated address constants, aliases, and inline helpers `tipc_addr`, `tipc_zone`, `tipc_cluster`, and `tipc_node`.

## Control Flow, State, and Integration

Runtime flow is socket creation/bind/connect/send/recv using service or socket addresses, topology subscription events, option get/set, link-name/node-id ioctls, and crypto key updates. State is TIPC cluster membership, service publications, subscriptions, group membership, bearer/link metadata, and AEAD keys.

## Risks and Test Signals

Risks include union decoding based on `addrtype`, flexible-array key sizing, deprecated address helper compatibility, scope value ambiguity, and not redacting crypto key payloads. Test signals include sockaddr decode for each address type, option and ancillary names, subscription/event structs, AEAD key length handling, and ioctl request formatting.
