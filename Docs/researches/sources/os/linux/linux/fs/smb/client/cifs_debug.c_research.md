# File Research: sources/os/linux/linux/fs/smb/client/cifs_debug.c

CIFS/SMB client debug and procfs implementation.

The file provides memory/MID dumping helpers, `/proc/fs/cifs/DebugData`, `open_files`, `open_dirs`, `Stats`, runtime toggles, security flag control, mount parameter listing, and optional SMB Direct tunables. When procfs is disabled, `cifs_proc_init()` and `cifs_proc_clean()` are empty.

DebugData walks global server/session/tcon structures under `cifs_tcp_ses_lock`, printing negotiated features, credits, dialects, compression/encryption, session security, multichannel state, tree connections, interfaces, pending MIDs, and SWN registrations. It calls protocol/server ops for dialect-specific details.

`open_files` reports tree/session/fid/flags/refcount/pid/uid/dentry plus lease cache state and lease key. `open_dirs` reports cached directory handles and, under `CONFIG_CIFS_DEBUG`, accepts write `0` to invalidate all cached dirs.

`Stats` reports allocation/resource counters and per-server/per-tcon statistics; writing a boolean resets counters and per-command timing under the appropriate locks.

Runtime proc knobs update `cifsFYI`, `traceSMB`, `linuxExtEnabled`, `lookupCacheEnabled`, and `global_secflags`. Security flag writes validate mask bits, normalize MUST-vs-MAY choices, prefer stronger MUST options, and ensure required signing implies signing allowed.
