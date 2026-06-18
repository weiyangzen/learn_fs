# File Research: sources/os/linux/linux/fs/lockd/netlink.h

Purpose: Auto-generated header for lockd generic netlink handlers and family object.

Key contents:
- Includes netlink/genetlink and lockd UAPI netlink definitions.
- Declares `lockd_nl_server_set_doit()`, `lockd_nl_server_get_doit()`, and external `lockd_nl_family`.

Dependencies and integration:
- Consumed by `netlink.c` and handler implementation code.
- Generated from `Documentation/netlink/specs/lockd.yaml`.

Risk notes:
- Must remain synchronized with generated `netlink.c` and UAPI command/attribute definitions.
