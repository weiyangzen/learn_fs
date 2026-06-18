# File Research: sources/os/linux/linux/fs/smb/client/cached_dir.c

Implements SMB2/SMB3 cached directory handles and cached directory-entry lifetime management.

`open_cached_dir()` is the central path: it finds or creates a `cached_fid`, converts the path to UTF-16, resolves a dentry, optionally uses a parent lease key, sends a compounded SMB2 CREATE plus QUERY_INFO, requires a lease with read caching, stores file-all-info, and returns a referenced cached handle. Replayable errors can retry with SMB2 replay markers.

The cache is keyed by path and stored under `cached_fids->entries`, protected by `cfid_list_lock`. A cached handle is usable only when `is_valid_cached_dir()` sees both `time` and `has_lease`; construction sets `has_lease` early so lease-break handling can safely consume the lease reference before the handle is visible.

Release paths are split carefully: `close_cached_dir()` is lock-safe external put, `close_cached_dir_locked()` is only for callers already holding `cfid_list_lock` and expecting at least two refs, and `smb2_close_cached_fid()` removes from lists, drops dentries, closes the SMB handle, and frees cache memory.

Invalidation occurs by name, by tcon reset, by lease break, by unmount, and by laundromat timeout. Lease breaks remove the entry, clear validity, take a tcon reference, drop the dentry asynchronously, then queue server-close work.

`free_cached_dir()` also frees cached dirents and subtracts tcon/global cache accounting. `init_cached_dirs()` initializes lists, counters, and delayed laundromat work; `free_cached_dirs()` cancels work and frees remaining active/dying entries.
