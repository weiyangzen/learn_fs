# sources/user-network-fs/samba/source4/torture/local/nss_tests.c

## Purpose
`nss_tests.c` validates NSS wrapper/user-group lookup consistency for passwd and group APIs, reentrant variants, membership expansion, and duplicate names.

## Important APIs, types, and functions
Helpers copy and print `struct passwd` and `struct group`, wrap `getpwnam`, `getpwnam_r`, `getpwuid`, `getpwuid_r`, `getgrnam`, `getgrnam_r`, `getgrgid`, `getgrgid_r`, `getpwent`, `getpwent_r`, `getgrent`, `getgrent_r`, and `getgrouplist`. Assertion helpers compare passwd/group records. Top-level tests cover enumeration, reentrant enumeration, cross-checks between reentrant and non-reentrant APIs, membership, and duplicate detection.

## Control flow
The enumeration tests require `NSS_WRAPPER_PASSWD` and `NSS_WRAPPER_GROUP`; otherwise they skip. They enumerate all users/groups, then verify each enumerated item can be retrieved by name and ID with matching fields. Membership compares `getgrouplist()` output to group membership lists, with documented skips for known local users and only full support for `ENVNAME=ad_member_idmap_rid:local`.

## State and persistence behavior
The tests are read-only against NSS databases. They allocate copied passwd/group records under the torture context and rely on environment variables pointing at wrapper files.

## Dependencies and integration points
The file depends on system NSS APIs through Samba replacement headers, optional platform macros for reentrant enumeration, environment variables from the selftest harness, and the local suite registry.

## Risks and edge cases
Behavior varies by platform: macOS may lack reentrant enumeration and Solaris has different function signatures. Membership tests document known AD member discrepancies and skip unsupported environments. Duplicate detection is O(n^2) but acceptable for test fixtures.

## Test signals
Passing tests show NSS wrapper enumeration is internally consistent, reentrant and non-reentrant calls agree, group membership expansion matches group lists for supported environments, and no duplicate user or group names are present.
