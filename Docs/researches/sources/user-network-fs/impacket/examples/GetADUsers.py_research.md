# sources/user-network-fs/impacket/examples/GetADUsers.py

## Purpose

`GetADUsers.py` queries Active Directory LDAP for user account information and prints account name, email, password-last-set time, and last-logon time. By default it returns enabled users with email addresses, with options to include all users or request one user.

## Important APIs, Types, and Functions

`GetADUsers.__init__` stores credentials, Kerberos/hash options, DC targeting, `-user`, `-all`, base DN, and table formatting. `getUnixTime` converts Windows FILETIME to Unix seconds. `processRecord` decodes `sAMAccountName`, `pwdLastSet`, `lastLogon`, and `mail`. `run` logs into LDAP, builds the search filter, runs a paged LDAP search, and closes the connection.

## Control Flow

CLI parsing feeds `parse_identity`; an empty domain aborts. `run` uses `ldap_login`, prints headers, and constructs a filter. Default mode requires `sAMAccountName`, `mail`, and not `UF_ACCOUNTDISABLE`; `-all` relaxes this to all users. If `-user` is supplied, the filter adds an `sAMAccountName` clause. Search results are streamed to `processRecord`, which converts FILETIME zero to `<never>` and otherwise formats local `datetime.fromtimestamp`.

## State and Persistence Behavior

The script performs read-only LDAP queries. It keeps credentials and output rows transiently and prints results. No files or directory state are modified.

## Dependencies and Integration Points

It depends on Impacket LDAP helpers, `ldapasn1`, SAMR `UF_ACCOUNTDISABLE`, and Active Directory attributes. It shares the standard Impacket example authentication pattern with Kerberos, hashes, AES keys, and DC host/IP options.

## Risks and Edge Cases

The `-all` filter string is missing a closing parenthesis until the later append, which works but is easy to break. The requested-user clause uses `(sAMAccountName:=%s)`, an unusual LDAP matching syntax that may not behave as intended compared with `(sAMAccountName=%s)`. Times use local timezone, not UTC. Attribute decoding assumes present values. Large domains depend on paged result behavior via `ldap.SimplePagedResultsControl`.

## Test Signals

Unit tests should cover filter construction for default, `-all`, `-user`, and combined cases; FILETIME conversion; disabled account filtering intent; missing mail/logon attributes; and per-record formatting. Integration tests require AD users with and without mail and disabled status.
