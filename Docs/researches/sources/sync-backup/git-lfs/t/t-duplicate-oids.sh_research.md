# sources/sync-backup/git-lfs/t/t-duplicate-oids.sh

## Purpose

Verifies that multiple revisions containing pointers with the same LFS OID produce only one upload during push, even when pointer text differs because one commit uses the legacy `http://git-media.io/v/2` pointer version and the next uses the current pointer format.

## Important APIs, control flow, and dependencies

The test uses `setup_remote_repo`, `clone_repo`, `git lfs track`, `calc_oid`, `pointer`, manual placement of media in `.git/lfs/objects`, two commits that change only pointer syntax around the same OID, and `git push origin main`. It delays the push until both commits exist so the server starts without the object.

## State, dependencies, integration points, risks, and test signals

State includes two Git revisions, one shared LFS object in the local cache, and no initial remote object. Integration points are pointer parsing for multiple spec URLs, pre-push object enumeration, duplicate OID collapse, and server object upload. The main risk is counting pointer blobs rather than unique OIDs, causing duplicate uploads or wrong progress totals. Signals are `Uploading LFS objects: 100% (1/1), 8 B` and `assert_server_object` for the shared OID.
