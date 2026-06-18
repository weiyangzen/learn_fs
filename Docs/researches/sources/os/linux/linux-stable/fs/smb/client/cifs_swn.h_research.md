# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_swn.h

## Purpose

Declares the CIFS Service Witness Protocol interface and provides no-op stubs when SWN upcall support is not configured.

## Main Contents

- Forward declares `struct cifs_tcon`, `struct sk_buff`, and `struct genl_info`.
- Under `CONFIG_CIFS_SWN_UPCALL`, declares:
  - `cifs_swn_register()`
  - `cifs_swn_unregister()`
  - `cifs_swn_notify()`
  - `cifs_swn_dump()`
  - `cifs_swn_check()`
- Defines inline server destination helpers:
  - `cifs_swn_set_server_dstaddr()` switches `server->dstaddr` to `server->swn_dstaddr` when `use_swn_dstaddr` is set.
  - `cifs_swn_reset_server_dstaddr()` clears `use_swn_dstaddr`.
- Without `CONFIG_CIFS_SWN_UPCALL`, provides no-op or false-returning inline stubs.

## Integration Notes

- Lets the rest of CIFS call witness hooks unconditionally while compiling out behavior when the feature is disabled.
- Destination-address helpers are still part of the conditional SWN behavior because they modify reconnect target selection.
