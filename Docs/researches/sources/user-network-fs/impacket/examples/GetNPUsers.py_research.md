# sources/user-network-fs/impacket/examples/GetNPUsers.py

## Purpose

`GetNPUsers.py` finds users with Kerberos pre-authentication disabled and optionally requests AS-REP material for offline cracking in hashcat or John format. It also supports directly testing usernames from a file without LDAP authentication.

## Important APIs, Types, and Functions

`GetUserNoPreAuth.printTable` formats LDAP result rows. `getTGT(userName, requestPAC=True)` manually builds an AS-REQ with `KERB_PA_PAC_REQUEST`, requests RC4 first and AES if RC4 is unsupported, decodes AS-REP versus KRB-ERROR, and formats encrypted AS-REP data. `run` chooses users-file, no-password direct request, LDAP enumeration, or fallback direct request paths. `request_users_file_TGTs` and `request_multiple_TGTs` drive batch output.

## Control Flow

The CLI parses a domain identity, `-request`, `-usersfile`, output format, output file, and authentication/DC options. In users-file mode, the script reads usernames and requests AS-REPs. In `-no-pass` direct mode, it requests for the supplied user without LDAP. Otherwise it attempts LDAP login, searches for enabled non-computer users with `UF_DONT_REQUIRE_PREAUTH`, prints attributes, and if requested, asks the KDC for each user's AS-REP. If LDAP authentication fails for reasons other than `strongerAuthRequired`, it tries to request the current user's AS-REP.

## State and Persistence Behavior

The script performs LDAP reads and KDC AS exchanges. It may write hash lines to `-outputfile`. It does not modify AD state, but incorrect use without `-no-pass` can cause authentication attempts against user accounts as noted in the usage text.

## Dependencies and Integration Points

It depends on Impacket LDAP helpers, Kerberos ASN.1 types, `sendReceive`, `KerberosError`, pyasn1 encoding/decoding, SAMR UAC constants, and AD/KDC behavior. Output formats integrate with hashcat and John the Ripper.

## Risks and Edge Cases

The code assigns `entry = self.getTGT(...)` in some branches but then calls `request_multiple_TGTs`, duplicating the request and ignoring `entry`. LDAP enumeration uses `sizeLimit=999` and comments that paged queries are not implemented, so large domains can be incomplete. Error handling relies on exception strings for NTLM negotiation guidance. AS-REP output contains crackable secret material and output files should be protected. FILETIME conversion uses local time.

## Test Signals

Unit tests can mock `sendReceive` to return KRB-ERROR, RC4 AS-REP, and AES AS-REP and verify hash formatting. LDAP tests should cover search filter construction, size-limit fallback, per-record parsing, users-file mode, and output file writing. Integration tests need a KDC/AD lab with preauth-disabled accounts.
