# sources/user-network-fs/samba/source4/torture/rpc/samr_priv.c

## Purpose

This file defines the `samr.priv` torture suite. It tests two authorization-sensitive SAMR behaviors: user-info caching after account deletion and access control for a non-privileged domain user attempting administrative SAMR operations.

## Important APIs, Types, and Functions

- `struct torture_user` describes a test user's identity, optional builtin memberships, and privilege intent.
- `struct torture_access_context` carries the authenticated SAMR pipe, user metadata, and join context for access tests.
- Basic SAMR helpers wrap name lookup, user creation, user open, domain open, connect, and `QueryUserInfo`.
- `torture_rpc_samr_caching()` creates a user, repeatedly opens and queries it on a second connection, deletes it, and then repeatedly verifies lookup/open behavior after deletion.
- `torture_rpc_samr_access_setup()` creates a normal test user, builds credentials, optionally adds builtin alias memberships, and opens an authenticated SAMR pipe as that user.
- `torture_rpc_samr_access()` attempts to create another user through the non-privileged pipe and requires failure.
- `torture_rpc_samr_priv()` registers `caching` and `access` under an SAMR RPC tcase.

## Control Flow

The caching test creates `guru0000`, then calls `test_samr_userinfo_getinfo()` twenty times with `expected=false`. Each iteration opens a new secondary SAMR connection, connects, opens the configured domain, opens the user by lookup RID, queries general user info, closes handles, and frees the pipe. After deleting the user, it repeats twenty calls with `expected=true`; the helper treats name lookup failure as success in that mode, checking that stale cache data does not allow a deleted user to be opened and queried.

The access test allocates a `torture_access_context`, creates a normal user `guru0100`, opens a SAMR connection authenticated as that user, and tries to create `guru0200` with `SEC_FLAG_MAXIMUM_ALLOWED`. The call must return false. Setup includes optional builtin alias membership code, but the registered access test does not populate memberships, so the membership branch is normally unused.

## State and Persistence Behavior

The file creates and deletes live domain users. It uses `torture_create_testuser()` and `torture_delete_testuser()` in the caching path, and `torture_create_testuser()` in the access path. The access path stores its join context but does not explicitly call a leave/delete helper in `torture_rpc_samr_access()`, so cleanup depends on talloc destructors or the broader torture join cleanup behavior. All other state is transient RPC handles and pipes.

## Dependencies and Integration Points

Dependencies include generated SAMR bindings, `dcerpc_pipe_connect()`, common torture RPC helpers, credential construction via `cli_credentials_*`, domain settings via `torture_setting_string()` and `lpcfg_workgroup()`, and shared `test_samr_handle_Close()` from the broader SAMR torture support. It integrates with the live domain account database and must run with initial credentials that can create/delete test accounts.

## Risks and Edge Cases

The caching test has fixed account names and can collide with stale accounts from prior failed runs. The `expected` parameter in `test_samr_OpenUser()` is counterintuitive: lookup failure returns true only when failure is expected. The optional builtin membership helper appears to zero `alias_handle` immediately before `samr_AddAliasMember`, which would invalidate the handle if that branch is exercised. The access test's lack of explicit cleanup is a persistence risk if join cleanup is not automatic.

## Test Signals

Caching passes when repeated query operations succeed before deletion and fail after deletion, indicating that server-side user caches invalidate deleted accounts. Access passes when an authenticated non-privileged user cannot create another account. Failures point to stale SAMR object caching, incorrect privilege enforcement, broken test-account lifecycle, or cleanup leakage.
