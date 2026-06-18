# sources/user-network-fs/impacket/tests/SMB_RPC/test_ldap.py

## Purpose

`test_ldap.py` provides remote integration tests for Impacket's LDAP client over LDAP and LDAPS. It validates login methods, searches, Kerberos authentication variants, and binary security descriptor round-tripping against Active Directory.

## Important APIs, Types, And Functions

The file imports `pytest`, `unittest`, `RemoteTestCase`, `impacket.ldap.ldap`, `ldapasn1`, `impacket.ldap.ldaptypes`, and `SR_SECURITY_DESCRIPTOR`. `LDAPTests` defines `connect()`, `tearDown()`, `dummySearch()`, and tests for security descriptors, Sicily package discovery, Sicily NTLM, SASL NTLM, Kerberos password login, Kerberos hash login, Kerberos AES-key login, NTLM hash login, and generic search. `LDAPTestsTCPTransport` and `LDAPTestsSSLTransport` are marked `pytest.mark.remote`.

## Control Flow

Transport subclasses call `set_transport_config(aes_keys=True)`, derive `url` from `serverName`, and build `baseDN` from the first two domain labels. `connect()` creates an `ldap.LDAPConnection` and optionally logs in. `dummySearch()` searches for `(servicePrincipalName=*)` and prints returned entries. `test_security_descriptor()` disables ACL size recalculation, searches computer objects for `nTSecurityDescriptor`, parses each descriptor with `SR_SECURITY_DESCRIPTOR`, dumps it, and asserts byte-for-byte round-trip. Authentication tests connect without initial login, invoke a specific login method, and usually run `dummySearch()`.

## State And Persistence Behavior

The tests keep a live `ldapConnection` attribute and close it in `tearDown()`. They do not intentionally modify directory objects, but depend on remote directory state, credentials, Kerberos material, and TLS configuration. `test_security_descriptor()` mutates global `impacket.ldap.ldaptypes.RECALC_ACL_SIZE = False` and does not restore it.

## Dependencies And Integration Points

These tests integrate with Impacket LDAP, ASN.1 LDAP message types, LDAP security descriptor structures, `RemoteTestCase`, pytest remote markers, Active Directory, NTLM/SASL/Sicily authentication, Kerberos KDC access, LM/NT hashes, AES keys, and LDAPS.

## Risks And Edge Cases

The tests are environment-sensitive and require a reachable AD server with valid remote-test configuration. `baseDN` assumes a two-label domain. Security descriptor comparison is binary-exact and can be affected by Windows padding, hence the global recalculation toggle. Printing search results can make logs noisy and expose directory data. Graceful skipping is delegated to pytest markers and `RemoteTestCase`, not handled locally.

## Test Signals

Passing tests signal working LDAP/LDAPS connectivity, simple/NTLM/SASL/Sicily/Kerberos authentication paths, search behavior, and security descriptor parse/serialize fidelity against a real domain. Mocked unit tests would be useful for deterministic descriptor and baseDN coverage.
