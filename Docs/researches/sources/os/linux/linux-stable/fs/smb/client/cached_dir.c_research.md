# File Research: sources/os/linux/linux-stable/fs/smb/client/cached_dir.c

## Purpose

Implements CIFS/SMB3 cached directory handles and cached directory-entry lifecycle, using SMB2 leases to reuse directory FIDs safely while handling lease breaks, reconnects, unmount cleanup, and periodic expiration.

## Main Responsibilities

- Creates and finds cached directory records:
  - `find_or_create_cached_dir()` searches `cfids->entries` by path, returns only valid leased entries, enforces `max_cached_dirs`, and creates new records when allowed.
  - `init_cached_dir()` allocates a `cached_fid`, duplicates the path, initializes work items, lists, mutexes, and kref.
- Resolves dentries:
  - `path_no_prefix()` strips CIFS prefix path when needed.
  - `path_to_dentry()` walks positive dentries from the CIFS root without permissions checks.
- Opens and populates cached handles:
  - `open_cached_dir()` converts paths to UTF-16, reserves/creates a cache slot, opens the directory with a lease, compounds `SMB2 CREATE` with `SMB2 QUERY_INFO`, validates lease/read-caching state, records file IDs and file-all-info, and returns a referenced cached FID.
  - `open_cached_dir_by_dentry()` finds an existing valid cached handle by dentry pointer.
  - Parent lease keys are supplied for SMB3 when a cached parent dentry is found.
- Drops cached handles:
  - `close_cached_dir()` drops a kref without holding `cfid_list_lock`.
  - `close_cached_dir_locked()` drops a reference while the list lock is held, with a `refcount >= 2` invariant.
  - `smb2_close_cached_fid()` removes the entry from lists, drops dentry, closes the server FID if open, and frees cached state.
  - `drop_cached_dir_by_name()` finds and invalidates a cached directory for removal paths.
- Handles broad invalidation:
  - `close_all_cached_dirs()` detaches dentries during unmount and flushes pending dentry-drop work.
  - `invalidate_all_cached_dirs()` moves entries to the dying list after session loss and schedules the laundromat.
  - `cached_dir_lease_break()` handles SMB lease breaks by removing the entry from lookup lists and queuing asynchronous cleanup.
- Implements periodic cleanup:
  - `cfids_laundromat_worker()` moves dying/expired cached FIDs to a local list, drops dentries, queues server close work when needed, and reschedules itself.
  - `free_cached_dirs()` cancels the laundromat and frees all remaining entries at tcon teardown.
- Tracks cached directory-entry memory accounting and decrements tcon/global counters when freeing cached entries.

## Key Data/Control Flow

- A cached FID is usable only when `is_valid_cached_dir()` sees both `time` and `has_lease`.
- New cache entries temporarily set `has_lease = true` during construction so an early lease break can consume the lease reference safely before the entry is fully valid.
- `open_cached_dir()` does not hold `cfid_list_lock` while sending SMB requests because reconnects may occur.
- On success, the cached FID gets a normal caller reference and a lease reference; on errors, it is removed from the list and references are unwound.
- Replayable SMB errors are retried through `smb2_should_replay()` and replay flags on both compounded requests.

## Concurrency and Lifetime Notes

- `cfids->cfid_list_lock` guards `entries`, `dying`, `num_entries`, and list membership flags.
- Krefs serialize final close/free; `kref_put_lock()` is used where the release function must remove entries while holding the spinlock.
- Dentry drops and server closes may be offloaded to `cfid_put_wq` and `serverclose_wq`.
- Tcon references are manually incremented/traced when queued work may outlive the immediate caller.

## Correctness and Risk Notes

- Lease state is central: entries without read-caching leases are rejected.
- Prefix-path stripping avoids double-prefixing when dentry lookup calls back into CIFS path construction.
- Unmount cleanup has an explicit OOM warning path where not all dentries may be dropped, risking "Dentry still in use" diagnostics.
