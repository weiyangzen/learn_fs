# sources/test-tools/strace/bundled/linux/include/uapi/linux/sock_diag.h

## Purpose

Defines common socket diagnostic netlink command ids, request headers, memory info indexes, destroy multicast groups, and BPF socket storage attributes. strace uses it as shared context for protocol-specific socket diagnostic headers.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. It exports netlink command ids `SOCK_DIAG_BY_FAMILY` and `SOCK_DESTROY`, `struct sock_diag_req`, `SK_MEMINFO_*` indexes, `enum sknetlink_groups`, BPF storage request/reply enums, and `SK_DIAG_BPF_STORAGE_*` nested attribute ids.

## Control Flow, State, and Integration

The flow is generic netlink-style socket diagnostics: request by family/protocol, optional destroy operation, and optional protocol-specific payloads. State is live socket table metadata and optional BPF local storage maps attached to sockets.

## Risks and Test Signals

Risks include misspelling compatibility (`SK_DIAB_BPF_STORAGE_REP_MAX` is exported as written), mixing request and reply BPF storage attribute namespaces, and assuming memory-info index count is fixed forever. Test signals include netlink decode for commands, `SK_MEMINFO_*` arrays, destroy groups, and BPF storage attributes.
