# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/daemon/acl_list.h

Unbound daemon header for client access control storage.

Core types:
- `enum acl_access`: deny/refuse variants, non-local restrictions, allow modes, set-RD allow, and cookie-gated allow.
- `struct acl_list`: regional allocator plus address tree.
- `struct acl_addr`: address tree node with ACL action, tag lists/actions/data, interface marker, and optional view pointer.

API:
- create/delete ACL list.
- insert listening interface ACL entries.
- apply normal and interface ACL config.
- lookup `acl_addr` by sockaddr and retrieve action.
- compute memory usage.
- convert ACL enum to string and log decisions.
- swap trees for reload-style replacement.

Role in group:
- Interface definition for Unbound’s downstream client policy engine, though `unwind` primarily uses its own frontend socket/process model.
