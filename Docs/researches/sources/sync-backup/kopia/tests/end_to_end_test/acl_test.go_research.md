# sources/sync-backup/kopia/tests/end_to_end_test/acl_test.go

## Purpose
End-to-end server ACL test covering default ACL setup, rule overwrites, user visibility, append-only behavior, retention, and credential refresh.

## Important APIs, Types, and Functions
Single `TestACL` uses `testenv.NewInProcRunner`, `server acl`, `server users`, `policy set`, `server start`, `server refresh`, and `clitestutil.ListSnapshotsAndExpectSuccess`.

## Control Flow
The test creates a server repository, enables ACLs, modifies default snapshot access, adds per-user snapshot/policy rules, creates users, starts a TLS server, connects three clients, and verifies each user's snapshot visibility and permissions. It also changes a user's password, refreshes server auth cache with admin credentials, verifies refresh fails with non-admin credentials, and reconnects with the new password.

## State and Persistence Behavior
Persists ACL manifests, user records, policies, snapshots, retention effects, and server auth cache state in a real repository. Multiple client configs connect to the same server.

## Dependencies and Integration Points
Integrates auth defaults, server control API, repository ACL evaluation, retention policy, snapshot creation/list/delete, TLS startup, and CLI password handling.

## Risks
Long, stateful, and order-dependent. Failure messages sometimes mention the wrong user in `Fatalf` text, but assertions are clear. Retention behavior under append access is subtle: server-side maintenance can keep latest snapshots while client delete is denied.

## Test Signals
Confirms default ACL count, duplicate rule rejection without overwrite, scoped read/append/full access, cross-user snapshot visibility, retention enforcement for append users, delete denial, and auth cache refresh requirements.
