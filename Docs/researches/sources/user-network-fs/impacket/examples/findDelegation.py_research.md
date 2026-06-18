# sources/user-network-fs/impacket/examples/findDelegation.py

## Purpose

`findDelegation.py` queries Active Directory LDAP data to report unconstrained delegation, constrained delegation with or without protocol transition, and resource-based constrained delegation (RBCD). It helps identify accounts and systems whose delegation settings create lateral movement paths, including cross-domain targeting through `-target-domain`.

## Important APIs, Types, and Functions

`checkIfSPNExists(ldapConnection, sAMAccountName, rights)` searches for either `HOST/<account>` or a delegated SPN and returns `Yes`, `No`, or `-`. `FindDelegation.printTable()` formats fixed-width output. `FindDelegation.__init__()` stores credentials, Kerberos settings, KDC host/IP, disabled-user filtering, requested account filtering, and builds the LDAP base DN from the target domain. `FindDelegation.run()` performs LDAP login, builds the delegation search filter, parses returned entries, resolves RBCD security descriptors, and prints result rows.

## Control Flow

CLI parsing uses `parse_identity()` for `domain[/username[:password]]`, initializes logging, determines the query domain, and instantiates `FindDelegation`. `run()` calls `ldap_login()` with FQDN mode, then searches for entries matching delegation-related LDAP attributes or UAC bits. It filters disabled accounts depending on `-disabled` and optionally narrows by `-user`.

For each `SearchResultEntry`, the script inspects `sAMAccountName`, `userAccountControl`, `objectCategory`, `msDS-AllowedToDelegateTo`, and `msDS-AllowedToActOnBehalfOfOtherIdentity`. RBCD values are parsed as `SR_SECURITY_DESCRIPTOR`; ACE SIDs are converted into a follow-up LDAP OR query so the delegating principals can be named. Results are collected as rows containing account, type, delegation type, rights target, and SPN existence.

## State and Persistence Behavior

The script is read-only against LDAP. It maintains local answer rows and temporary per-entry parsing state. No local cache or output file is written. Cross-domain mode clears explicit KDC host/IP settings because a single custom KDC setting can break referral ticket processing.

## Dependencies and Integration Points

It depends on Impacket LDAP helpers, LDAP ASN.1 result types, SAMR UAC constants, and `ldaptypes.SR_SECURITY_DESCRIPTOR`. It integrates with AD LDAP schema attributes and security descriptor ACL parsing. The output is plain text intended for operator workflows and can be consumed by scripts if column widths remain stable.

## Risks and Edge Cases

The LDAP filter is string-built and only lightly constrained; unusual `sAMAccountName` values supplied through `-user` are not escaped. `printTable()` assumes at least one data row and all rows have the same width, though it is only called when results exist. RBCD parsing assumes a present DACL and does not guard each ACE shape. LDAP search uses `sizeLimit=999` without paging, so large domains can produce incomplete results. Attribute order assumptions appear in the RBCD follow-up response when reading `attributes[0]` and `attributes[1]`.

## Test Signals

Tests should mock LDAP search responses for each delegation type, disabled filtering, target-user filtering, empty results, and `sizeLimitExceeded` handling. RBCD tests should include multiple ACEs, missing DACLs, disabled delegating accounts, and SPN-existence lookups. Integration signals are successful LDAP bind with NTLM, Kerberos, hashes, AES keys, and cross-domain query behavior.
