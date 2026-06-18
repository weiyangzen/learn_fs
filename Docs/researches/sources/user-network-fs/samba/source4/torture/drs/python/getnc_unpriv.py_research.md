# sources/user-network-fs/samba/source4/torture/drs/python/getnc_unpriv.py Research

## Purpose
This module tests `DsGetNCChanges` authorization behavior for users with no replication rights, only `DS-Replication-Get-Changes`, only `DS-Replication-Get-Changes-All`, or both rights. It covers single-object replication, secret replication, full NC replication, invalid DNs, OU-as-NC requests, and partial attribute sets.

## Important APIs, Types, And Functions
`DrsReplicaSyncUnprivTestCase.setUp()` creates a random OU, creates a test user, binds as administrator and as that user, builds ACE strings for `GUID_DRS_GET_CHANGES` and `GUID_DRS_GET_ALL_CHANGES`, saves the original base DN security descriptor, and disables Kerberos for the new user credentials to avoid KDC replication races. `tearDown()` restores the original security descriptor and tree-deletes the OU.

Helper methods `_test_repl_exop()`, `_test_repl_single_obj()`, `_test_repl_secret()`, `_test_repl_full()`, and `_test_repl_full_on_ou()` build request8 payloads with `DRSUAPI_DRS_WRIT_REP`, send them through the unprivileged DRS handle, and either expect success or catch `WERRORError` with a permitted error set.

## Control Flow
Each test grants a specific ACL state on the domain base DN and runs the same request family. With only GET_CHANGES, most single-object and secret requests are denied, full replication is denied, but partial attribute set requests can succeed. With only GET_ALL_CHANGES, the module deliberately reuses no-rights expectations. With both rights, valid single-object and full replication succeed while invalid DNs and REPL_SECRET keep documented error expectations. With no rights, all replication forms are rejected, allowing some Samba/Windows error precedence variability.

## State And Persistence
The test creates a user and OU and modifies the domain base DN security descriptor by adding object-specific control-access ACEs. It stores and restores the original SDDL, which is critical because teardown failure could leave elevated replication rights. Temporary objects are tree-deleted.

## Dependencies And Integration Points
The module depends on `drs_base`, `samba.tests`, `sd_utils.SDUtils`, generated DRSUAPI/security constants, Samba credentials, LDB, and werror exception types. It integrates directly with DRSUAPI request8 and AD security descriptors.

## Risks And Test Signals
Signals are success/no-exception for permitted requests and exact WERROR families for denied or invalid requests. Risks include security descriptor restoration failure, Samba/Microsoft error precedence differences, race avoidance by disabling Kerberos rather than waiting for replication, and reliance on random OU names to avoid stale cleanup collisions.
