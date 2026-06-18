# sources/user-network-fs/impacket/examples/badsuccessor.py

## Purpose

`badsuccessor.py` is an Impacket example for delegated Managed Service Account (dMSA) and BadSuccessor-related Active Directory operations. It can search OUs for identities with rights that may enable the attack, add a dMSA linked to a target account, modify that link, or delete the dMSA.

## Important APIs, Types, and Functions

`BADSUCCESSOR.__init__` stores credentials, LDAP/LDAPS method, target/DC settings, action, dMSA options, base DN, target OU, principals allowed, target account, and DNS hostname. `run` initializes LDAP and dispatches `add_dmsa`, `delete_dmsa`, `modify_dmsa`, or `search_ous`. `search_ous` reads OU security descriptors and identifies relevant ACEs. `is_excluded_sid` and `resolve_sid_to_name` filter/resolve identities. `convert_sid_to_string` and `build_security_descriptor` construct dMSA membership descriptors. `add_dmsa`, `modify_dmsa`, and `delete_dmsa` perform LDAP mutations.

## Control Flow

The CLI validates action-specific required arguments, parses credentials via `parse_target` or `parse_identity`, initializes logging, then runs `BADSUCCESSOR`. `run` derives `baseDN`, chooses LDAP or LDAPS, handles Kerberos DC host/IP selection, binds through `init_ldap_session`, and dispatches. Search mode first looks for Windows Server 2025 domain controllers, then queries OUs with security descriptors, parses DACL ACEs for create-child/generic-all/write-DACL/write-owner rights and dMSA object-specific GUIDs, filters high-privilege built-in/domain admin SIDs, resolves remaining SIDs, and prints identities and OUs. Add mode builds a dMSA object and security descriptor for the allowed principal, resolves a target account DN, and adds the LDAP object. Modify mode replaces `msDS-ManagedAccountPrecededByLink`. Delete mode removes the object.

## State and Persistence Behavior

Search mode is read-only but reads security descriptors. Add/modify/delete modes mutate AD by creating, changing, or deleting dMSA objects and links. The script may create security descriptors granting rights to a selected principal. It keeps only in-memory LDAP connection and option state locally.

## Dependencies and Integration Points

It depends on `ldap3`, Impacket LDAP session helpers, Impacket `ldaptypes` security descriptor/ACE/SID structures, UUID conversion for object-specific ACE GUIDs, and AD schema features for `msDS-DelegatedManagedServiceAccount`. It is specifically tied to Windows Server 2025 dMSA behavior for exploitation relevance.

## Risks and Edge Cases

This is high-impact AD mutation code. LDAP filters interpolate user-supplied values without escaping, which can break searches or permit LDAP filter injection in lab tooling contexts. `if ('operatingSystem' and 'operatingSystemVersion') not in entry` is logically flawed because it only checks the second string. Domain SID may be undefined if lookup fails, yet later filtering references it. In `add_dmsa`, after finding a preferred user/computer target DN, the code immediately assigns the first entry DN again, potentially overriding the preference. Several exceptions are swallowed in OU parsing, which can hide descriptor parsing gaps. Search output is heuristic and does not prove exploitability by itself.

## Test Signals

Unit tests should cover SID conversion, security descriptor construction, excluded SID filtering, well-known SID resolution, object GUID parsing from ACEs, LDAP filter construction, add/modify/delete attribute dictionaries, and the target-DN selection bug. Integration tests require a Windows Server 2025 AD lab with OUs carrying specific ACEs and permissions to create/modify/delete dMSAs.
