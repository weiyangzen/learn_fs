<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/leases_util.c -->
# sources/user-network-fs/samba/source3/locking/leases_util.c

## Purpose
`leases_util.c` provides small helpers that translate legacy oplock state into SMB2 lease state and retrieve the effective lease type for a `files_struct`.

## Important APIs, Types, And Functions
`map_oplock_to_lease_type` maps `BATCH_OPLOCK`, `EXCLUSIVE_OPLOCK`, and `LEVEL_II_OPLOCK` combinations to SMB2 lease READ/WRITE/HANDLE bits. `fsp_lease_type` returns the effective lease state for a file handle, using the direct oplock-to-lease mapping for non-lease oplocks and `leases_db_get_current_state` for real SMB2 leases. `fsp_client_guid` returns the per-client GUID from the connection's server connection client global.

## Control Flow
For non-`LEASE_OPLOCK` handles, `fsp_lease_type` is pure and returns a mapping from `fsp->oplock_type`. For `LEASE_OPLOCK`, it queries `leases.tdb` using the current file's client GUID and lease key, passing `fsp->leases_db_seqnum` so unchanged database state can avoid a full update. Failures are logged at debug level and collapse the cached `fsp->lease_type` to no lease.

## State And Persistence
This file owns no persistent storage, but it reads and updates per-handle cached fields `fsp->leases_db_seqnum` and `fsp->lease_type`. It relies on `leases.tdb` sequence numbers to keep the cache coherent.

## Dependencies And Integration Points
It depends on open-files NDR constants, `locking/proto.h`, smbd globals, and `leases_db.h`. `strict_lock_check_default` in `locking.c` uses `fsp_lease_type` to bypass strict byte-range checks when a read or write lease makes the check unnecessary.

## Risks And Test Signals
The mapping is security and correctness sensitive because returning too broad a lease can skip strict lock checks. The failure path deliberately returns no lease, which is conservative but may hurt performance. Test signals include every oplock combination, lease database sequence cache hits/misses, lease break state changes, missing lease records, and strict-locking `Auto` behavior for read and write I/O.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/leases_util.c -->
