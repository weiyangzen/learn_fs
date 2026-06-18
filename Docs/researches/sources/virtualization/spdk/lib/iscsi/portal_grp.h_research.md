# File Research: sources/virtualization/spdk/lib/iscsi/portal_grp.h

Full-file read: 78 lines.

This header defines portal and portal-group data structures and management APIs.

Main contents:
- `struct spdk_iscsi_portal`: group pointer, bounded host/port buffers, listener socket, per-group/global queue links.
- `struct spdk_iscsi_portal_grp`: refcount, tag, public/private flag, CHAP settings, socket group, acceptor poller, and portal list.
- Public/private semantics for login redirection are documented in the structure comments.
- Declares create/destroy/register/unregister/find/open/close/info/config APIs and redirect address parsing.

Integration points:
- Consumed by RPC, target-node mapping, subsystem lifecycle, and connection accept paths.

Risks and review notes:
- Refcount is an integer field managed manually by target-node mappings.
- Public/private redirect behavior depends on target-node code honoring `is_private`.

Testing focus:
- Structure lifecycle through portal group create/map/delete.
- Refcount behavior when portal groups are removed while targets reference them.
