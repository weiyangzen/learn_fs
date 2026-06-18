# sources/user-network-fs/samba/source4/torture/ldap/uptodatevector.c

## Purpose

`uptodatevector.c` tests that local modifications to partition root metadata do not unexpectedly change `replUpToDateVector`. It covers default, configuration, and schema naming contexts.

## Important APIs, Types, and Functions

- `test_check_uptodatevector()` reads a partition root, decodes `replUpToDateVector`, modifies `description` twice, rereads the vector, and compares raw blob stability.
- `ndr_pull_replUpToDateVectorBlob()` decodes the vector for validation/debug printing.
- `torture_ldap_uptodatevector()` connects and runs the check for three partition roots.

## Control Flow

For each partition DN, the helper searches base-scope for `uSNChanged`, `replUpToDateVector`, and `description`, decodes the current vector if present, then performs two `ldb_modify()` calls replacing `description`. After each modify it rereads the same attributes, decodes the vector, compares presence, length, and bytes against the original, prints status, and marks failure if the vector changed.

## State and Persistence Behavior

This test intentionally modifies the `description` attribute on partition root objects. It does not restore the previous description. It expects `uSNChanged` and description to change while `replUpToDateVector` remains stable.

## Dependencies and Integration Points

It depends on LDAP-backed LDB, command-line credentials with write access, DSDB partition base DN helpers, NDR DRS blob decoding, and the LDAP suite registration.

## Risks and Edge Cases

Because it writes partition root descriptions and does not restore them, it can leave visible test values. Required permissions are higher than read-only LDAP tests. Vector absence/presence and raw byte ordering must remain stable across expected local metadata updates.

## Test Signals

Success is printed as `replUpToDateVector[not changed: ok]` for both modifications on all three partitions. Any decoded vector change, decode error, search count mismatch, or modify failure is a regression signal.
