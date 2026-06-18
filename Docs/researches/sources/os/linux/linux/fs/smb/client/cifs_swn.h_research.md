# File Research: sources/os/linux/linux/fs/smb/client/cifs_swn.h

Header for CIFS Service Witness Notification support.

When `CONFIG_CIFS_SWN_UPCALL` is enabled, it declares register/unregister/notify/dump/check functions and provides helpers to temporarily use `server->swn_dstaddr` as `server->dstaddr`.

When disabled, it provides no-op inline stubs so callers can compile without feature-specific conditionals.
