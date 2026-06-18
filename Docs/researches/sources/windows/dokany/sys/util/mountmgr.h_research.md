# File Research: sources/windows/dokany/sys/util/mountmgr.h

Header for Dokan Mount Manager helper APIs.

Key responsibilities:
- Declares mount point notification helpers for persistent volume symbolic links.
- Declares AutoMount query and set helpers.
- Declares volume-arrival notification.
- Declares the generic Mount Manager IOCTL send helper.
- Declares directory mount point created/deleted wrappers.
- Declares explicit mount point create and delete-point operations.

Dependencies:
- Includes `../dokan.h` for Dokan device/control block types.
- Includes `<mountmgr.h>` for Mount Manager constants and structures.
- Implemented by `mountmgr.c` and called from mount initialization and teardown paths.

Notable risks:
- Comments contain spelling issues such as “persistante” and “MountManage,” but the API intent is clear.
- The generic IOCTL helper exposes raw buffers and lengths, so callers must construct Mount Manager variable-length structures exactly.
