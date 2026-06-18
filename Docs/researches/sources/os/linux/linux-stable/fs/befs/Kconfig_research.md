# File Research: sources/os/linux/linux-stable/fs/befs/Kconfig

## Purpose
Defines kernel configuration options for BeOS File System support.

## Main Contents
`BEFS_FS` is a tristate read-only BeFS driver option depending on `BLOCK` and selecting `BUFFER_HEAD` and `NLS`. Help text describes BeFS as BeOS’s native 64-bit filesystem with attributes and database-like indices, while noting this driver does not expose those advanced features.

`BEFS_DEBUG` is a boolean dependent on `BEFS_FS` that enables driver debug output when the debug mount option is used.

## Risks / Review Notes
This is configuration metadata only. The read-only status is explicitly part of the user-facing option text and should remain accurate if write support ever changes.
