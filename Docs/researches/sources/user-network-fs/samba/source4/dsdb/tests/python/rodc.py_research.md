# sources/user-network-fs/samba/source4/dsdb/tests/python/rodc.py

## Purpose

This script tests direct LDAP write behavior against a read-only domain controller. It verifies that add, modify, and delete attempts that should be handled by a writable DC are rejected by the RODC with LDAP referrals, and that those referrals point to a concrete writable DC rather than only the domain DNS name. It also verifies that deleting a nonexistent object returns `ERR_NO_SUCH_OBJECT` instead of referral.

## Important APIs, Types, and Functions

The main class is `RodcTests(samba.tests.TestCase)`. `setUp()` opens a `SamDB` connection to `HOST` with system session and command-line credentials, stores the domain DN, reads `dsServiceName` from the rootDSE, and creates a unique UUID tag for temporary object names.

Test methods:

- `test_add_replicated_objects()` attempts to add an OU, user, group, and `NTDSConnection` object through the RODC. Each add must fail with `ERR_REFERRAL`; the test extracts the referred `ldap://...` URL, connects to it, proves the same operation works there, and deletes the created object.
- `test_modify_replicated_attributes()` attempts to modify replicated attributes (`carLicense`, `middleName`) on the Guest account and expects referrals. It then applies the modification on the referred DC.
- `test_modify_nonreplicated_attributes()` attempts to modify non-replicated logon/counter attributes (`badPwdCount`, `lastLogon`, `lastLogoff`). Windows refers these too, so Samba is expected to refer them.
- `test_modify_nonreplicated_reps_attributes()` reads and unpacks `repsFrom`, mutates `result_last_attempt`, repacks it, and verifies the attempted replace is referred.
- `test_delete_special_objects()` tries to delete Guest and expects referral.
- `test_no_delete_nonexistent_objects()` ensures nonexistent delete is a local `ERR_NO_SUCH_OBJECT`.
- `main()` parses host/options, normalizes bare host or file paths to LDAP/TDB URLs, and runs `TestProgram`.

## Control Flow

Most tests follow the same pattern: attempt a write through `self.samdb`, catch `LdbError`, require `ldb.ERR_REFERRAL`, parse the referred LDAP URL with a regex, and reject referrals that lack a concrete DC host. Add and replicated-attribute modify tests additionally connect to the referral target and prove the write works on that target. Non-replicated and delete tests only validate referral shape.

The `repsFrom` test adds NDR-specific flow: it reads the binary replication metadata, unpacks it with `ndr_unpack(drsblobs.repsFromToBlob, ..., allow_remaining=True)`, changes a field, and repacks with `ndr_pack()` before attempting the modify.

## State and Persistence Behavior

The test is intended to avoid durable state on the RODC. Successful referred add tests create temporary objects on a writable DC and delete them immediately. Replicated attribute modifications against Guest are applied to the referral target and are not restored by this script, so they can persist until overwritten by later tests or environment reset. The unique UUID tag reduces naming collision risk for add/delete objects.

## Dependencies and Integration Points

The script depends on Samba's `SamDB`, `system_session`, subunit test runner, `ldb` error constants and message APIs, NDR packing/unpacking, and DRS replication blob structures. It integrates with AD topology via rootDSE `dsServiceName`, domain DNS name detection, and referral URLs returned by the server.

## Risks and Edge Cases

Referral parsing is regex-based and assumes the server returns an `ldap://...>` substring. A referral format change can fail the test even if semantic referral behavior is correct. The check `address.lower().startswith(self.samdb.domain_dns_name())` is intended to reject nonspecific referrals, but URL formatting differences could affect it. The test writes to Guest attributes on the referred writable DC without cleanup, which is acceptable in isolated test environments but risky in shared directories.

## Test Signals

Passing results show that an RODC refuses writes by referral, that referrals target an actual writable DC, and that nonexistent deletes are resolved locally as no-such-object. Failures indicate regressions in RODC write routing, referral construction, DRS metadata protection, or LDAP error mapping.
