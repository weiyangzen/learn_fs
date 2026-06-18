# sources/user-network-fs/samba/source4/torture/rpc/samr_accessmask.c

## Purpose

This file defines two SAMR torture suites. `torture_rpc_samr_accessmask()` checks the server-side interpretation of access masks on SAMR connect handles, domain lookup/open calls, domain enumeration, and policy-handle security descriptors. `torture_rpc_samr_workstation_auth()` verifies that a machine workstation account can perform common read-oriented SAMR queries while requesting `SEC_FLAG_MAXIMUM_ALLOWED`, matching winbind and other Samba client behavior.

The tests are protocol compatibility and authorization tests rather than unit tests. They exercise a live SAMR endpoint, create temporary accounts, authenticate with user or machine credentials, and assert specific `NTSTATUS` results for access-mask combinations.

## Important APIs, Types, and Functions

- Local helpers `torture_samr_Close()` and `torture_samr_Connect5()` wrap `dcerpc_samr_Close_r()` and `dcerpc_samr_Connect5_r()` and return the operation result after transport success.
- `test_samr_accessmask_Connect5()` iterates one-bit masks and asserts which bits can obtain a connect handle.
- `test_samr_accessmask_EnumDomains()`, `test_samr_accessmask_LookupDomain()`, and `test_samr_accessmask_OpenDomain()` verify that only specific connect-handle rights allow those follow-up operations.
- `test_samr_connect_user_acl()` reads the SAMR policy security descriptor, attempts to add a deny ACE for a test user with `SAMR_ACCESS_CONNECT_TO_SERVER`, verifies the user can still connect, and verifies the descriptor did not change despite `SetSecurity` success.
- `test_samr_connect_user_acl_enforced()` authenticates as the test user and expects a request for `SAMR_ACCESS_SHUTDOWN_SERVER` to fail.
- `test_samr_domain()`, `test_samr_users()`, `test_samr_groups()`, and `test_samr_aliases()` enumerate and query domain objects for the workstation-auth suite.
- The suite builders use `torture_suite_add_rpc_iface_tcase()` for ordinary SAMR tests and `torture_suite_add_machine_workstation_rpc_iface_tcase()` for machine-authenticated SAMR tests.

## Control Flow

The accessmask suite registers five tests. The bitmask tests all follow a similar pattern: loop through 33 one-bit masks, call `Connect5`, branch on the bit position, then either require the connect/open/query call to succeed or require `NT_STATUS_ACCESS_DENIED`. Successful handles are explicitly closed. `OpenDomain` first obtains the current domain SID via a maximum-allowed connect handle, then repeats the bitmask loop using that SID.

The ACL tests run through `test_samr_connect()`. A temporary normal user is created with `torture_create_testuser()`, credentials are assembled with `cli_credentials_*`, and the user SID is read from the join context. The test then checks that `SetSecurity` on a SAMR connect handle does not persistently modify the server descriptor and that the descriptor is still enforced for an ordinary user's requested access. Cleanup is via `torture_leave_domain()`.

The workstation-auth suite starts with a machine workstation tcase. `torture_rpc_samr_workstation_query()` opens a SAMR connection, opens the workgroup domain, queries domain info, walks display-info users, domain groups, and aliases, and opens/queries each object where applicable.

## State and Persistence Behavior

The file intentionally mutates external server state by creating and deleting `samr_testuser` and by creating a temporary workstation account named from `TEST_MACHINENAME`. It also calls `samr_SetSecurity` against a connect handle, but the expected behavior is that this does not persistently change the SAMR policy descriptor. Handles are closed after successful paths, and test-user cleanup relies on Samba torture join helpers.

No local persistent state is written. All durable effects are on the target server under test, so failed or interrupted runs can leave temporary domain accounts until the test harness cleanup runs.

## Dependencies and Integration Points

This file depends on generated SAMR NDR client bindings (`ndr_samr_c.h`), torture RPC helpers (`torture_rpc.h`), loadparm/workgroup settings, and security descriptor helpers from `libcli/security/security.h`. It integrates with the Samba torture suite registry through exported suite constructors and relies on common test join helpers for user and machine account lifecycle. It also uses `lpcfg_workgroup()` and `torture_setting_string()` to bind assertions to the active test domain.

## Risks and Edge Cases

The bit-position expectations encode default SAMR ACL semantics and may be sensitive to server policy changes, Samba3 behavior, or non-standard domain ACLs. The test explicitly skips `test_samr_connect()` against Samba3. The workstation-auth path assumes a domain with exactly one non-builtin domain when auto-enumerating, well-formed display info, and queryable users/groups/aliases.

The loop uses `uint32_t mask` and shifts through 33 iterations; after bit 31, the next shift wraps to zero. The tests are written around bit positions rather than symbolic rights, making maintenance error-prone when SAMR rights change. Several failure paths return before closing handles or freeing temporary pipes, which is acceptable for a terminating torture test but can complicate repeated in-process runs.

## Test Signals

Strong pass signals are exact `NTSTATUS` matches for access-denied cases, successful close calls on opened handles, unchanged security descriptor size after `SetSecurity`, successful ordinary-user denial for shutdown access, and successful workstation-authenticated enumeration/query of users, groups, aliases, and domain info. Failures indicate regressions in access-mask mapping, SAMR policy descriptor handling, machine-account authorization, or compatibility with Windows/Samba SAMR semantics.
