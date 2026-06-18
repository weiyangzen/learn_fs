# sources/user-network-fs/impacket/examples/CheckLDAPStatus.py

## Purpose

`CheckLDAPStatus.py` enumerates domain controllers through DNS SRV records, then checks each controller for LDAP signing enforcement and LDAPS channel binding token policy. It is an unauthenticated or low-auth diagnostic tool for Active Directory LDAP hardening posture.

## Important APIs, Types, and Functions

`CheckLDAP.__init__` stores the domain, resolver/DC IP, and DNS timeout. `list_dc` uses `dns.resolver.Resolver` to query `_ldap._tcp.dc._msdcs.<domain>` SRV records. `run` iterates controllers. `check_ldap_signing` attempts unsigned LDAP login via `LDAPConnection(..., signing=False)`. `check_ldaps_cbt` uses LDAPS, manipulates `LDAPConnection.channel_binding_value`, and classifies errors into `Never`, `When Supported`, `Always`, or `No TLS cert`.

## Control Flow

CLI parsing requires `-dc-ip` and `-domain`. After logger initialization, `CheckLDAP.run` resolves DC hostnames, logs the count, and for each one performs the signing and CBT checks. LDAP signing is considered required when an unsigned bind produces `strongerAuthRequired`. LDAPS CBT starts with no channel binding value; an `80090346` LDAP error means required, a bad-credential `52e` response prompts a second bind with a deliberately corrupted CBT to distinguish `When Supported`, and TLS reset errors are mapped to missing certificate.

## State and Persistence Behavior

The script keeps only in-memory status strings and prints results. It creates short-lived LDAP/TLS connections and DNS queries. No files are written and no directory state is modified.

## Dependencies and Integration Points

It depends on `dnspython`, `pyOpenSSL`, Impacket LDAP classes, Impacket example logging, and an accessible DNS/DC IP. It integrates with Active Directory SRV discovery, LDAP port 389, and LDAPS port 636 behavior.

## Risks and Edge Cases

Policy detection is based on string matching LDAP error text, which can change with localization or library formatting. `check_ldaps_cbt` mutates byte index 15 of the CBT and assumes a sufficiently long binding value. Blank username binds may behave differently across DC policy, anonymous bind settings, and NTLM restrictions. DNS failures abort the whole run. Results are policy inference, not authoritative LDAP configuration reads.

## Test Signals

Tests need integration fixtures or mocked `LDAPConnection` and DNS resolver behavior. Useful cases include SRV enumeration, `strongerAuthRequired`, bad credentials without signing requirement, CBT required error, corrupted-CBT error, TLS reset/no certificate, and unexpected LDAP errors under debug logging.
