# File Research: sources/os/linux/linux/fs/nfs/nfs40proc.c

## Purpose
Defines NFSv4.0 minor-version procedure behavior, including sequence slot handling, lease renewal, migration recovery, lockowner release, and state recovery operation tables.

## Key Behavior
- `nfs40_call_sync_prepare()` / `nfs40_call_sync_done()` wrap synchronous calls with v4 sequence setup and completion.
- `nfs40_sequence_done()` frees v4.0 sequence slots.
- `nfs40_open_expired()` clears delegation state and recovers open state without v4.1-style delegation recovery.
- Async and sync RENEW paths maintain leases and schedule recovery on lease moved, lease recovery, or callback path down errors.
- `_nfs40_proc_get_locations()` and `_nfs40_proc_fsid_present()` support migration and lease-moved recovery with appended RENEW.
- `nfs4_release_lockowner()` sends RELEASE_LOCKOWNER asynchronously for v4.0 lock state cleanup.

## Operation Tables
Defines v4.0 sequence slot ops, reboot recovery ops, no-grace recovery ops, state renewal ops, migration recovery ops, and the exported `nfs_v4_0_minor_ops`.

## Research Notes
This file is v4.0 state-machine glue. The main maintenance risks are slot release ordering, lease renewal timestamps, recovery scheduling on specific NFS4 errors, and v4.0-only lockowner release behavior.
