# sources/sync-backup/git-lfs/t/t-batch-unknown-oids.sh

## Purpose
Tests that the transfer queue rejects a server response containing an unknown OID. The repository name `unknown-oids` triggers the test server to return a response inconsistent with the requested object set.

## Important APIs, Functions, and Control Flow
The test creates a remote repository, tracks `*.dat`, commits an object whose content is `unknown-oid`, attempts to push, captures the exit code, verifies the server did not receive the object, and requires a specific error message in `push.log`.

## State, Persistence, and Dependencies
State includes the local commit, `.gitattributes`, server object store, and `push.log`. It depends on `setup_remote_repo`, `clone_repo`, `calc_oid`, and `refute_server_object`.

## Integration Points, Risks, and Test Signals
The integration point is validation of batch API responses before object upload. Signals are nonzero push status, absent server object, and `[unknown-oid] The server returned an unknown OID.` Risks are dependence on test-server repository-name behavior and exact message text.
