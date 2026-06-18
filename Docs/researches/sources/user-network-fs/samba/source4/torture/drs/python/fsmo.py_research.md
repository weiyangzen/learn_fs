# sources/user-network-fs/samba/source4/torture/drs/python/fsmo.py Research

## Purpose
This module tests FSMO role transfer through `samba-tool fsmo transfer` for schema, infrastructure, PDC, RID, naming, DomainDnsZones, and ForestDnsZones roles. It verifies transfers between DCs and no-op behavior when the target already owns a role.

## Important APIs, Types, And Functions
`DrsFsmoTestCase.setUp()` caches each DC's `dsServiceName` and builds role owner DNs. `_net_fsmo_role_transfer()` runs `samba-tool fsmo transfer --role=<role> -H ldap://<DC>:389` using the current Kerberos ccache. `_wait_for_role_transfer()` polls `fSMORoleOwner` until it matches the expected service name. `_role_transfer()` transfers to DC2, transfers back to DC1, and performs a no-op transfer to DC1.

## Control Flow
Each `test_*Transfer()` method calls `_role_transfer()` with a role name and DN. The shared scenario checks command success and then polls LDAP for the expected `fSMORoleOwner` on the relevant DC. Polling uses a 20 second maximum with 0.2 second sleeps.

## State And Persistence
The test changes real FSMO ownership in the test domain and attempts to restore each role to DC1. A failure between transfer and transfer-back can leave roles on DC2. No custom directory objects are created.

## Dependencies And Integration Points
The module depends on `drs_base`, LDB base searches, SambaTool command execution, Kerberos ccache credentials, and two DCs able to transfer all listed roles.

## Risks And Test Signals
Signals are successful command exit, expected stdout text, empty stderr, and `fSMORoleOwner` matching target service names. Risks include role ownership left changed on failure, timing-sensitive polling, and possible role DN construction issues for DNS application partitions because the formatted DN strings include embedded spaces.
