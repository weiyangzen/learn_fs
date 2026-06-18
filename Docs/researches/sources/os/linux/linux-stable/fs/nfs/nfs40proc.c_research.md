# File Research: sources/os/linux/linux-stable/fs/nfs/nfs40proc.c

## Purpose
Defines NFSv4.0 minor-version procedure behavior: sequence slot handling, renewals, migration recovery, lock-owner release, state recovery operations, and the exported `nfs_v4_0_minor_ops`.

## Sequence Handling
- `nfs40_call_sync_prepare()` sets up v4 sequence state before sync calls.
- `nfs40_call_sync_done()` completes sequence processing.
- `nfs40_sequence_free_slot()` returns or reassigns a slot in the v4.0 slot table.
- `nfs40_sequence_done()` frees sequence slot when present.

## State and Delegation Recovery
- `nfs40_clear_delegation_stateid()` clears delegation stateid when a delegation exists.
- `nfs40_open_expired()` clears delegation/open state flags and calls generic expired-open recovery. NFSv4.0 does not allow delegation recovery on open expiration.
- `nfs40_test_and_free_expired_stateid()` returns `-NFS4ERR_BAD_STATEID`, reflecting lack of v4.1-style TEST_STATEID/FREE_STATEID support.

## Lease Renewal
- `struct nfs4_renewdata` tracks client and timestamp.
- `nfs4_proc_async_renew()`
  - Queues asynchronous RENEW when renewal flags are nonzero.
  - Takes a client ref and records timestamp.
- `nfs4_renew_done()`
  - Handles success, `LEASE_MOVED`, callback path down, and general lease recovery scheduling.
  - Calls `do_renew_lease()` on successful/handled renew.
- `nfs4_proc_renew()`
  - Synchronous RENEW and lease timestamp update.

## Migration and Lease-Moved Recovery
- `_nfs40_proc_get_locations()`
  - Sends FS_LOCATIONS with appended RENEW to signal migration recovery.
  - Fills `nfs4_fs_locations`.
  - Renews server lease on success.
- `_nfs40_proc_fsid_present()`
  - Sends FSID_PRESENT with appended RENEW to signal lease-moved recovery.
  - Allocates temporary file handle result storage.
  - Updates lease on success.

## Lock Owner Release
- `struct nfs_release_lockowner_data` stores lock state, server, args/res, and timestamp.
- `nfs4_release_lockowner_prepare()` sets up sequence and lock owner clientid.
- `nfs4_release_lockowner_done()` renews lease on success or schedules recovery/retry for stale clientid, expired lease, lease moved, or delay.
- `nfs4_release_lockowner_release()` frees lock state and calldata.
- `nfs4_release_lockowner()` queues asynchronous RELEASE_LOCKOWNER for minor version 0 only.

## Exported Minor Version Ops
- `nfs_v4_0_minor_ops`
  - minor version: 0
  - initial capabilities: READDIRPLUS, ATOMIC_OPEN, POSIX_LOCK
  - client init/shutdown: `nfs40_init_client()`, `nfs40_shutdown_client()`
  - stateid match/root sec/lock state/free expired hooks
  - seqid allocator and sync/sequence slot ops
  - reboot and no-grace recovery ops
  - lease renewal ops
  - migration recovery ops

## Research Notes
This file adapts generic NFSv4 state machinery to v4.0 constraints: no sessions, v4.0 slot table behavior, RENEW-based lease maintenance, SETCLIENTID-era recovery, and RELEASE_LOCKOWNER support.
