# File Research: sources/os/linux/linux/fs/quota/netlink.c

Generic netlink notification support for quota warnings.

Key responsibilities:
- Defines the `VFS_DQUOT` generic netlink family with one multicast group, `events`.
- Implements `quota_send_warning()`, exported for quota core and other filesystems.
- Sends warning attributes:
  - quota type,
  - exceeded quota ID,
  - warning type,
  - device major/minor,
  - current UID that caused the event.

Important behavior:
- Uses `GFP_NOFS` allocation because warnings are emitted from filesystem write/accounting paths, where filesystem reclaim recursion can deadlock.
- Uses `from_kqid_munged(&init_user_ns, qid)` and `from_kuid_munged()` so messages can always carry usable IDs.
- Registers the generic netlink family at `fs_initcall`.

Research notes:
- This file is notification-only; the actual warning decision logic is in `dquot.c`.
