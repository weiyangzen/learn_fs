# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/share_config.h

Read status: complete.

## Purpose
Defines cached share configuration state and helper APIs.

## Main Contents
- `struct ksmbd_share_config` with name, path, flags, veto list, resolved `struct path`, refcount, hash node, create/directory masks, and forced UID/GID fields.
- Invalid UID/GID sentinels.
- Inline helpers for create and directory mode calculation.
- Flag testing and share config get/put/delete APIs.
- Veto filename match API.

## Dependencies And Role
Consumed by tree connections and VFS create/path handling.

## Risks
Refcounted share configs own resolved paths and veto lists. Mode helper behavior depends on Samba-like mask/force semantics.
