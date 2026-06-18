# sources/user-network-fs/samba/source3/include/locking.h

## Purpose
`locking.h` defines the byte-range lock record formats and context identifiers used by smbd locking code. It documents the on-disk/in-TDB shape of `brlock.tdb` records and separates Windows-style and POSIX-style byte-range locks.

## Important APIs, Types, And Control Flow
Key enums are `brl_type` (`READ_LOCK`, `WRITE_LOCK`, `UNLOCK_LOCK`) and `brl_flavour` (`WINDOWS_LOCK`, `POSIX_LOCK`). `struct lock_context` identifies a client lock namespace with SMB lock context, tree id, and `server_id`. `struct lock_struct` is the stored linear record containing context, start, size, fnum, lock type, and flavor. `struct smbd_lock_element` is a request-oriented representation with GUID, SMB lock context, type, flavor, offset, and count. The header forward-declares `files_struct`, `byte_range_lock`, and `share_mode_lock`.

## State And Persistence
The important persistent state is `brlock.tdb`: records are unsorted linear arrays of `lock_struct` values, with count derived from TDB record size. `UNLOCK_LOCK` is explicitly not stored and exists for POSIX unlock range computation. The `server_id` dependency lets lock ownership survive multi-process smbd coordination.

## Dependencies And Integration Points
It depends on generated `server_id` and `misc` NDR headers plus `lib/file_id.h`. It integrates with byte-range lock code, share mode locking, file handle state, POSIX lock downgrades, and oplock/share-mode decisions.

## Risks And Test Signals
Risks include ABI/layout mismatch for existing TDB data, incorrect range math for unlocks, stale `server_id` ownership after process death, and semantic mismatch between Windows and POSIX lock flavors. Test signals include overlapping read/write lock conflict tests, POSIX unlock range splitting, lock downgrade re-evaluation, TDB record migration/reading, smbd process death cleanup, and mixed clients using Windows and POSIX locking on the same file.
