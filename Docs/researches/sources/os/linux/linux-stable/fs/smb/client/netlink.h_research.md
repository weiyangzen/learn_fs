# File Research: sources/os/linux/linux-stable/fs/smb/client/netlink.h

Read status: complete.

## Purpose

Declares the CIFS generic netlink family and its lifecycle functions.

## Main Contents

- Include guard `_CIFS_NETLINK_H`.
- `extern struct genl_family cifs_genl_family`.
- `int cifs_genl_init(void);`
- `void cifs_genl_exit(void);`

## Dependencies

- Intended for CIFS client code that needs access to the generic netlink family or registration helpers.

## Role in the Subsystem

This is the small public internal header for `netlink.c`, separating CIFS netlink registration declarations from the implementation.
