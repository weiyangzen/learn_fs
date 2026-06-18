# sources/user-network-fs/impacket/examples/dacledit.py

## Purpose
`dacledit.py` reads, backs up, restores, writes, and removes ACEs in an Active Directory object's DACL over LDAP. It targets common AD privilege-management operations such as granting FullControl, ResetPassword, WriteMembers, DCSync, or custom GUID/mask rights to a selected principal.

## Important APIs, Types, and Functions
`DACLedit` is the main class. Its constructor stores target/principal selectors, initializes `ldapdomaindump.domainDumper`, resolves principal SIDs when needed, fetches target `nTSecurityDescriptor`, and parses masks. `read()`, `write()`, `remove()`, `backup()`, and `restore()` are the user-facing operations. Security descriptor work is done with `impacket.ldap.ldaptypes.SR_SECURITY_DESCRIPTOR`, `ACE`, `ACCESS_ALLOWED_ACE`, `ACCESS_ALLOWED_OBJECT_ACE`, and related mask classes.

Enum classes define rights GUIDs, ACE flags, object ACE flags, access mask values, simple permissions, and object ACE mask flags. `parseDACL()`, `parseACE()`, `parsePerms()`, `printparsedDACL()`, and `printparsedACE()` implement display. `create_ace()` and `create_object_ace()` build new ACEs. `modify_secDesc_for_dn()` performs LDAP `MODIFY_REPLACE` with `security_descriptor_control(sdflags=0x04)`.

## Control Flow
The CLI parses authentication, target, principal, and DACL action options. `main()` rejects write without a principal and restore without a file, authenticates through `parse_identity()` and `init_ldap_session()`, constructs `DACLedit`, then dispatches on `-action`. Reads fetch and parse the DACL. Writes append generated ACEs to the local DACL, backup the current descriptor, then replace the remote descriptor. Removes build comparison ACE templates, filter matching ACEs out of the local DACL, backup, and replace only if a match was found. Restore reads a JSON backup, backs up the current target, and pushes the saved descriptor.

## State and Persistence
Remote state changes are LDAP security descriptor replacements on AD objects. Local persistence comes from backup files containing JSON with `sd` as hex-encoded raw security descriptor bytes and `dn` as the target DN. If no filename is supplied, timestamped `dacledit-YYYYMMDD-HHMMSS.bak` files are created; existing filenames are not overwritten.

## Dependencies and Integration Points
The script depends on `ldap3`, `ldapdomaindump`, Impacket LDAP security descriptor types, `msada_guids`, and shared Impacket LDAP session helpers. It integrates with AD LDAP/LDAPS, security descriptor controls, schema and extended-right GUID catalogs, and Kerberos/NTLM authentication.

## Risks
This is a high-impact privilege modification tool. Incorrect target/principal selectors or custom masks can grant or remove dangerous rights. `remove()` compares structural fields and object GUIDs but can miss semantically equivalent ACEs or remove more than expected if a template is too broad. `restore()` trusts backup JSON assertions and descriptor content. There is a latent `elif args.action == 'flush'` branch even though argparse does not expose `flush`. Some conditionals rely on `and`/`or` precedence and should be tested carefully.

## Test Signals
Unit tests can validate ACE construction for allowed/denied, inherited and non-inherited flags, DCSync GUID expansion, custom mask parsing, and ACE removal matching. Integration tests need an AD lab object, read-only and write-capable accounts, backup/restore round trips, insufficient-rights failures, DN/SID/sAMAccountName target lookup, and adminCount inheritance behavior.
