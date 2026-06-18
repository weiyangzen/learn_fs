# sources/user-network-fs/samba/source4/dsdb/tests/python/sites.py

## Purpose

`sites.py` tests Samba AD site and subnet management helpers against a live directory. It validates `samba.sites` site creation/deletion semantics, `samba.subnets` subnet creation, deletion, rename, and site reassignment, permission failures for non-admin users, and a large Windows-compatible CIDR validation matrix for IPv4 and IPv6 subnet names.

## Important APIs, Types, and Functions

`SitesBaseTests` opens a system-session `SamDB`, captures the domain DN, domain SID, and configuration DN, and provides `get_user_dn()`. `SimpleSitesTests` calls `sites.create_site()` and `sites.delete_site()` and expects `SiteAlreadyExistsException`, `SiteNotFoundException`, and `SiteServerNotEmptyException` in duplicate, missing, and non-empty-site cases. `SimpleSubnetTests` creates two temporary sites in a transaction, removes them in teardown, and exercises `subnets.create_subnet()`, `delete_subnet()`, `rename_subnet()`, and `set_subnet_site()`.

The helper `get_user_and_ldb()` creates a temporary non-admin user, constructs sealed non-Kerberos `Credentials`, binds a separate `SamDB`, and registers cleanup for the user. It is used to assert that subnet create, rename, and delete operations fail with `ERR_INSUFFICIENT_ACCESS_RIGHTS`.

## Control Flow

The script parses a host, normalizes it to LDAP when needed, opens `SamDB` with command-line credentials and `system_session`, then runs Subunit tests. Site tests perform simple create/delete operations. Subnet tests set up two sites, create subnets under the configuration NC, search by `objectclass=subnet` and `cn=<cidr>`, and verify either object disappearance or updated `siteObject`.

CIDR validation is the largest control-flow block. `test_create_bad_ranges()` iterates invalid values, expecting `subnets.SubnetInvalid`; any accepted CIDR is deleted and recorded as a failure. `test_create_good_ranges()` iterates valid values, expects creation, verifies exactly one matching subnet exists, and deletes it. The matrices include network-bit alignment, mask range, address octet range, malformed strings, embedded NULs, type errors, leading zeros, RFC5952 canonicalization, IPv4-embedded IPv6 behavior, reserved ranges, and Windows-specific exclusions such as bitmask-looking IPv4 addresses.

## State and Persistence Behavior

The file creates and removes AD Sites container children and Subnets container children in the configuration partition. The setup transaction creates `testsite` and `testsite2`, and teardown deletes them. Individual subnet tests delete created subnets explicitly. Non-admin tests create `notadmin` under `CN=Users` and remove it via cleanup. Because test CIDRs are reused, failed cleanup can affect later test runs.

## Dependencies and Integration Points

The suite integrates with `samba.sites`, `samba.subnets`, `SamDB`, LDB searches, Samba credentials, GENSEC sealing, and LDAP access control enforcement. It depends on configuration partition schema and default `CN=Sites` layout. It also depends on `subnets` helper exception contracts, not just raw LDAP errors, so it is a regression test for helper API behavior.

## Risks and Edge Cases

The CIDR tests encode exact Samba/Windows compatibility choices that differ from general IP library acceptance rules. Updating validation code to follow only RFC behavior can break these tests. The non-admin username is fixed, so leftover objects can cause setup noise if cleanup fails. The tests assume enough administrative privilege to create sites and subnets and assume `Default-First-Site-Name` contains servers. Some malformed inputs are non-string Python objects; validation must reject before string-specific operations crash unexpectedly.

## Test Signals

Pass signals include duplicate and missing site/subnet operations raising the documented Samba exceptions, non-admin operations failing specifically with `ERR_INSUFFICIENT_ACCESS_RIGHTS`, rename leaving no old subnet object, site reassignment changing `siteObject`, all invalid CIDRs being rejected, and all valid CIDRs creating exactly one LDAP subnet object.
