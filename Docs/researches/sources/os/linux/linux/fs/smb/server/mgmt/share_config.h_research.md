# File Research: sources/os/linux/linux/fs/smb/server/mgmt/share_config.h

This header defines `struct ksmbd_share_config` and share configuration helpers.

Key fields:
- Share name/path and path length.
- Share flags and veto-list.
- Resolved `struct path`.
- Atomic refcount and hash node.
- Create/directory masks and forced create/directory modes.
- Forced uid/gid fields, with invalid sentinels.

Inline helpers compute final create/directory modes by applying masks and forced bits, and test share flags. Public APIs fetch, put, delete, and veto-match shares.
