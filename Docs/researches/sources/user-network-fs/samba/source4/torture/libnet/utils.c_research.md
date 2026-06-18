# sources/user-network-fs/samba/source4/torture/libnet/utils.c

## Purpose
`utils.c` provides shared SAMR/LSA and LDAP helper functions for libnet torture tests, including domain open, user/group create and cleanup, handle close, libnet context initialization, and monitor-message printing.

## Important APIs, types, and functions
`test_domain_open()` performs SAMR connect, domain lookup, and open. `_get_account_name_for_user_rdn()` uses LDAP/LDB to find `sAMAccountName` for a user RDN. `test_user_cleanup()` and `test_group_cleanup()` delete accounts through SAMR. `test_user_create()` and `test_group_create()` create accounts and recover from existing stale objects. `test_samr_close_handle()`, `test_lsa_close_handle()`, `test_libnet_context_init()`, and `msg_handler()` support common test setup and async diagnostics.

## Control flow
Domain open establishes a SAMR connection handle, looks up the domain SID, opens a domain handle, optionally returns the SID, and closes the connect handle. Account cleanup resolves names to RIDs, opens the user or group, and deletes it. Create helpers retry by deleting stale users/groups if the server returns already-exists. Context initialization optionally opens SAMR and LSA pipes and stores their binding handles in `libnet_context`.

## State and persistence behavior
The helpers mutate persistent directory state by creating and deleting users and groups. `_get_account_name_for_user_rdn()` opens an LDAP connection to the configured host but is read-only. Handles are remote state and must be explicitly closed; helper failures can leave accounts or handles until connection teardown.

## Dependencies and integration points
The file integrates SAMR/LSA generated RPC clients, `ldb_wrap_connect`, command-line credentials, torture RPC connection helpers, loadparm settings, and monitor message types from libnet. It is the foundation for most files in `source4/torture/libnet`.

## Risks and edge cases
Cleanup correctness depends on LDAP lookup finding the right `sAMAccountName`, especially after account renames. Recreate-on-exists logic is useful for stale state but dangerous if a fixed test name collides with a real account. Context setup returns partially initialized state on connection failures only after freeing the context.

## Test signals
Helper success is a prerequisite for user, group, and domain libnet tests. The functions also verify direct SAMR create/delete/open/close behavior while supporting higher-level libnet API checks.
