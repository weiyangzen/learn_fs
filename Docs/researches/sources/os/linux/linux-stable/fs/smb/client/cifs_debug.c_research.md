# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_debug.c

## Purpose

Implements CIFS/SMB client debug dumping, `/proc/fs/cifs` diagnostics and tunables, statistics reset/reporting, open-file/open-directory reporting, security-flag control, mount-parameter introspection, and optional RDMA debug tunables.

## Main Responsibilities

- Raw debug helpers:
  - `cifs_dump_mem()` prints hex dumps.
  - `cifs_dump_mids()` prints pending MID request details under `CONFIG_CIFS_DEBUG2`.
- Tcon/server/session formatting:
  - `cifs_debug_tcon()` reports share mount count, filesystem type, device info, path limits, status, encryption, POSIX extensions, witness, sparse behavior, reconnect state, and DFS origin path.
  - `cifs_dump_channel()` reports multichannel connection details.
  - `cifs_dump_iface()` reports server interface speed, RSS/RDMA capabilities, IP address, cleanup state, channel allocation, and connection state.
- `/proc/fs/cifs/open_files`:
  - `cifs_debug_files_proc_show()` lists tree/session/FID/flags/count/pid/uid/name plus lease state, lease key, and optional MID.
- `/proc/fs/cifs/open_dirs`:
  - `cifs_debug_dirs_proc_show()` lists cached directory handles and per-cache dirent accounting.
  - Under `CONFIG_CIFS_DEBUG`, writes of `0` invalidate all cached directories across CIFS mounts.
- `/proc/fs/cifs/DebugData`:
  - `cifs_debug_data_proc_show()` prints CIFS version, compiled feature set, buffer size, active request count, servers, sessions, channels, shares, interfaces, pending MIDs, compression/encryption state, and SWN registrations.
- `/proc/fs/cifs/Stats`:
  - `cifs_stats_proc_show()` reports allocation/resource counts, reconnect counts, active XID stats, per-server request stats, and per-tcon operation stats.
  - `cifs_stats_proc_write()` resets statistics and reconnect counters.
- Proc tunables:
  - `cifsFYI` controls CIFS debug verbosity bitmask.
  - `traceSMB` toggles SMB tracing.
  - `LinuxExtensionsEnabled` toggles legacy Linux extensions.
  - `LookupCacheEnabled` toggles lookup-cache behavior.
  - `SecurityFlags` validates and sets global security policy flags.
  - `mount_params` lists supported SMB3 mount parameters and parameter types.
- Proc registration:
  - `cifs_proc_init()` creates `/proc/fs/cifs` entries.
  - `cifs_proc_clean()` removes them.
  - Stubs are provided when `CONFIG_PROC_FS` is disabled.

## Key Data/Control Flow

- Most proc output walks the global `cifs_tcp_ses_list`, then nested session, tcon, open-file, channel, and MID lists.
- Global/session/tcon locks are taken around list traversal and mutable fields:
  - `cifs_tcp_ses_lock`
  - `server->srv_lock`
  - `ses->ses_lock`
  - `ses->chan_lock`
  - `ses->iface_lock`
  - `tcon->tc_lock`
  - `tcon->open_file_lock`
  - `server->mid_queue_lock`
  - cached-dir list locks
- Feature lines are controlled by compile-time Kconfig symbols.
- Security flag writes support boolean shortcuts and numeric flags, reject zero/unsupported flags, normalize MUST flags, and imply MAY_SIGN when signing is required.

## Security and Exposure Notes

- Key dumping is controlled by separate Kconfig (`CIFS_DEBUG_DUMP_KEYS`) elsewhere, but debug output still exposes session IDs, user IDs, server names, share names, FIDs, and network addresses.
- `/proc/fs/cifs/open_files` is mode `0400`; writable debug/tunable entries are generally `0644` or `0600` for `open_dirs` with debug enabled.
- `SecurityFlags` writes directly affect global CIFS module security behavior.

## Integration Notes

- Relies heavily on `seq_file` helpers from `fs/seq_file.c`.
- Integrates optional DFS, SMB Direct, SWN, compression, stats2, legacy, POSIX, upcall, and xattr features through preprocessor gates.
- Calls `cifs_swn_dump()` so witness registrations appear in DebugData.
