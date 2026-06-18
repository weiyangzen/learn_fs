# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_debug.h

## Purpose

Defines CIFS debug/logging macros, debug levels, exported debug-control variables, and debug helper prototypes.

## Main Contents

- Resets `pr_fmt` to prefix messages with `CIFS:`.
- Declares debug helpers:
  - `cifs_dump_mem()`
  - `cifs_dump_mids()`
  - `dump_smb()`
- Declares global controls:
  - `traceSMB`
  - `cifsFYI`
- Defines debug-level bits:
  - `CIFS_INFO`, `CIFS_RC`, `CIFS_TIMER`
  - message classes `VFS`, `FYI`, optional `NOISY`, and `ONCE`.
- Under `CONFIG_CIFS_DEBUG`, defines:
  - `cifs_info()`
  - `cifs_dbg()`
  - `cifs_server_dbg()`
  - `cifs_tcon_dbg()`
  - Each supports rate-limited or once-only logging and routes VFS messages to error logs, FYI/NOISY to debug logs.
- Without `CONFIG_CIFS_DEBUG`, debug macros compile to unreachable `pr_debug()` forms while preserving format checking; `cifs_info()` remains active.

## Integration Notes

- `cifs_server_dbg()` takes `server->srv_lock` to safely print the hostname.
- `cifs_tcon_dbg()` tolerates null tcon/tree names.
- Used throughout CIFS client code for consistent logging policy.
