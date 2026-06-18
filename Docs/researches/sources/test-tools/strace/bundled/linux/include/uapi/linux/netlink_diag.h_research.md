# sources/test-tools/strace/bundled/linux/include/uapi/linux/netlink_diag.h

Purpose: defines the socket-diagnostic ABI for inspecting netlink sockets through `NETLINK_SOCK_DIAG`. It supplies request/response structs, ring configuration structs, optional diagnostic attributes, show masks, and socket flag bits.

Important APIs/types/functions: `struct netlink_diag_req` contains family, protocol selector, inode, `ndiag_show` bitmask, and cookie filter. `struct netlink_diag_msg` reports family, socket type, netlink protocol, connection state, source/destination port IDs, destination group, inode, and cookie. `struct netlink_diag_ring` mirrors mmap ring sizing. Attribute enum values cover memory info, multicast groups, RX/TX rings, and flags. `NDIAG_PROTO_ALL` selects all protocols; `NDIAG_SHOW_*` controls optional data; `NDIAG_FLAG_*` reports socket options such as packet info, broadcast error, no-ENOBUFS, listen-all-nsid, and cap-ack.

Control flow: a diagnostic client sends `netlink_diag_req`, often via sock_diag with `sdiag_family = AF_NETLINK`; the kernel replies with one or more `netlink_diag_msg` records and optional netlink attributes requested by `ndiag_show`. The strace decoder in `src/netlink_netlink_diag.c` first prints the fixed request/response fields, then uses `NLMSG_ALIGN(sizeof(msg))` to locate optional attributes and dispatches to decoders for meminfo, groups, ring config, and flags.

State/persistence behavior: diagnostic messages are snapshots of live netlink sockets. There is no durable state; cookies and inode fields let userspace correlate a returned socket with kernel socket identity at the moment of the dump. Ring attributes expose current mmap RX/TX ring configuration if requested.

Dependencies/integration: includes `<linux/types.h>` and relies on the generic sock_diag/netlink infrastructure. In strace it integrates with `netlink_sock_diag.h`, `src/netlink_sock_diag.c`, `src/socketutils.c`, and generated xlats `netlink_diag_attrs`, `netlink_diag_show`, `netlink_socket_flags`, and `netlink_states`. Tests include `tests/netlink_sock_diag.c`, `tests/netlink_netlink_diag.c`, and `tests/nlattr_netlink_diag_msg.c`.

Risks: request and response structs share similar field names but different semantics; decoders must not treat `sdiag_protocol` and `ndiag_protocol` identically when printing `NDIAG_PROTO_ALL`. Group attributes are word-size dependent, so 32-bit and 64-bit decoding can differ. `NDIAG_SHOW_RING_CFG` is deprecated but still part of the ABI and xlat coverage. Optional attributes require strict length checks to avoid reading past short diagnostic payloads.

Test signals: expected output should decode `NDIAG_SHOW_*` masks, `NETLINK_DIAG_*` attributes, `NDIAG_FLAG_*` flags, ring fields, cookies, and `NDIAG_PROTO_ALL`. Short-message tests should show ellipses or raw addresses rather than corrupt field output.
