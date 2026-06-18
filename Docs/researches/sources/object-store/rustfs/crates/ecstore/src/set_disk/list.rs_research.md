# sources/object-store/rustfs/crates/ecstore/src/set_disk/list.rs

## Purpose
Provides a small set-wide recursive delete helper. Despite the filename, this file currently contains `SetDisks::delete_all`, used by heal and bucket cleanup code to remove a prefix from every disk in a set.

## Important APIs, Types, And Functions
`delete_all(&self, bucket, prefix) -> Result<()>` clones the current disk vector, calls `DiskAPI::delete` with `DeleteOptions { recursive: true }` on each online disk, records errors, and returns `Ok(())` regardless of collected disk failures.

## Control Flow
The method reads `self.disks`, clones the vector to release the lock, builds one async delete future per disk, and awaits all with `join_all`. Missing disks are represented as `DiskError::DiskNotFound`; successful deletes push `None` into the local `errors` vector and failures push `Some(error)`.

## State And Persistence Behavior
The only persisted effect is best-effort recursive deletion of the requested bucket/prefix on every available disk. The accumulated `errors` vector is not reduced against write quorum and is not logged, so callers cannot tell whether all, some, or no disks deleted the prefix.

## Dependencies And Integration Points
Depends on `DiskStore`, `DiskAPI::delete`, and `DeleteOptions` from the set-disk module prelude. It is used by healing to remove temporary UUID directories and by store bucket deletion to clean metadata prefixes.

## Risks
Returning success unconditionally can hide cleanup failures and leave temporary or metadata objects on a subset of disks. For healing, stale temp directories may waste capacity; for bucket metadata cleanup, partial deletion can leave inconsistent internal state. If callers require quorum semantics, they need a stricter helper.

## Test Signals
No tests in this file. Useful tests would inject per-disk delete failures and assert intended best-effort behavior or enforce a future quorum/error-reporting contract.
