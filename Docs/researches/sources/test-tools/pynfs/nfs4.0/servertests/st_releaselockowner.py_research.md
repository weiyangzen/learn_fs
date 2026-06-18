# sources/test-tools/pynfs/nfs4.0/servertests/st_releaselockowner.py

Purpose: Tests `RELEASE_LOCKOWNER` for a normal unlocked owner, an owner whose file has been removed after unlock, and rejection while locks are still held.

Important APIs/types/functions: Imports `lock_owner4`, `nfs_ops.NFS4ops.release_lockowner`, and `environment.check`. Public tests are `testFile`, `testFile2`, and `testLocksHeld`.

Control flow: Each test initializes a connection, creates a confirmed file, locks it with a named lock owner, and either unlocks before release or attempts release while the lock remains. `testFile2` removes the file before releasing the lock owner.

State and persistence behavior: Mutates lock owner state, lock records, and in one case removes the locked file after unlocking.

Dependencies and integration points: Depends on lock support and the client's current confirmed `clientid` to construct `lock_owner4(c.clientid, owner_bytes)`.

Risks: Servers that garbage collect lock owners aggressively or tie owners to removed files differently may expose edge behavior. The test expects locks-held protection before owner release.

Test signals: Success for unlocked release paths and `NFS4ERR_LOCKS_HELD` when trying to release an owner with an active lock.
