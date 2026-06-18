# File Research: sources/os/linux/linux/fs/smb/client/netlink.h

## Purpose
Declares the CIFS generic netlink family and registration lifecycle functions.

## Main Contents
- Header guard `_CIFS_NETLINK_H`.
- `extern struct genl_family cifs_genl_family`.
- Prototypes for `cifs_genl_init()` and `cifs_genl_exit()`.

## Integration Points
Included by the netlink implementation and module initialization code that registers/unregisters CIFS generic netlink support.

## Risks And Review Focus
- This header is intentionally minimal; changes should remain aligned with `netlink.c` and generic netlink lifecycle call sites.
