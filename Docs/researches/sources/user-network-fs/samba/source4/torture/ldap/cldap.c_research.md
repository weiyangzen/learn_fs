# sources/user-network-fs/samba/source4/torture/ldap/cldap.c

## Purpose

`cldap.c` tests generic connectionless LDAP operations over UDP port 389. It verifies a Samba CLDAP server answers RootDSE searches with common attributes, netlogon attributes, and false filters without transport or protocol errors.

## Important APIs, Types, and Functions

- `ldap_msg_to_ldb()` converts an LDAP search entry to an `ldb_message` for LDIF dumping.
- `cldap_dump_results()` prints CLDAP results through LDB LDIF helpers when debug logging is high.
- `test_cldap_generic()` resolves the target host, creates a `cldap_socket`, and performs several `cldap_search()` calls.
- `torture_cldap()` runs the generic test for the configured `host`.

## Control Flow

The test resolves the NetBIOS server name to an IP, creates a `tsocket_address` for UDP 389, initializes a CLDAP socket, and sends searches for whole RootDSE, selected `currentTime`/`highestCommittedUSN`, those attributes plus `netlogon`, `netlogon` alone, and a false expression involving `highestCommittedUSN=2`. Each request expects `NT_STATUS_OK`; optional debug output dumps entries as LDIF.

## State and Persistence Behavior

The file is read-only and connectionless. All state is per-request search input/output and temporary LDB conversion state for printing.

## Dependencies and Integration Points

Dependencies include `libcli/cldap`, raw LDAP structures, NetBIOS name resolution, `tsocket`, LDB LDIF utilities, and torture LDAP registration. It is exposed as `ldap.cldap`.

## Risks and Edge Cases

False-filter behavior is only checked for transport success, not exact entry count. Result dumping steals LDAP attribute arrays into an LDB message for printing, so it is debug-path sensitive. Resolution failures or UDP filtering can fail the test before server logic is reached.

## Test Signals

The main signal is `NT_STATUS_OK` from every CLDAP search variant. Debug LDIF output can help confirm RootDSE and netlogon attributes are present and decodable.
