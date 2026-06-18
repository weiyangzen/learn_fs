# sources/user-network-fs/impacket/examples/owneredit.py

## Purpose

`owneredit.py` reads or modifies the owner SID (`OwnerSid`) in an Active Directory object’s `nTSecurityDescriptor`. It is intended for scenarios where a caller has rights to inspect or change object ownership and wants to specify both target object and new owner by sAMAccountName, SID, or distinguished name.

## Important APIs, Types, and Functions

`WELL_KNOWN_SIDS` maps common SID strings to display names. `OwnerEdit` stores LDAP session/server objects, target selectors, new-owner selectors, and a `ldapdomaindump.domainDumper` used to locate the domain root. `search_target_principal_security_descriptor()` queries only owner information with `security_descriptor_control(sdflags=0x01)`. `read()` formats the current owner SID and resolves sAMAccountName/DN. `write()` replaces `OwnerSid` in an `ldaptypes.SR_SECURITY_DESCRIPTOR` and writes `nTSecurityDescriptor` with LDAP modify plus the owner-only security descriptor control. `resolveSID()` uses the well-known SID map first and LDAP `objectSid` lookup as fallback.

## Control Flow

`parse_args()` builds authentication, owner, target, and action options. `main()` validates that write has a new owner selector, parses credentials with `parse_identity`, initializes an LDAP or LDAPS session through `init_ldap_session`, constructs `OwnerEdit`, and runs `read` or `read` then `write`. Constructor logic resolves the target security descriptor immediately when target args exist and resolves new owner SID from sAMAccountName or DN when a raw SID was not provided.

## State and Persistence Behavior

Read mode is side-effect free. Write mode persists a changed owner SID to the target object’s `nTSecurityDescriptor` in Active Directory. Local state is only the parsed descriptor and LDAP lookup results. The script does not write files and does not maintain rollback data.

## Dependencies and Integration Points

The script depends on `ldap3`, `ldapdomaindump`, `ldap3.protocol.microsoft.security_descriptor_control`, Impacket `ldaptypes`, and example utilities `init_ldap_session`/`parse_identity`. It integrates with AD LDAP/LDAPS and requires appropriate directory permissions, especially `WRITE_OWNER` or equivalent control over the target.

## Risks and Edge Cases

The constructor condition `if self.new_owner_SID is None and self.new_owner_sAMAccountName is not None or self.new_owner_DN is not None` relies on Python precedence; DN lookup will run even when a SID is also supplied. The DN LDAP filters are not escaped in all paths. `read()` assumes owner SID can be found in LDAP and may fail for built-in or foreign SIDs after logging a well-known mapping. `main()` contains stale restore-action validation for an action that argparse does not expose. Failed writes log LDAP result messages but do not exit non-zero explicitly.

## Test Signals

Useful tests include selector precedence for target by sAMAccountName/SID/DN, new-owner resolution by all supported forms, well-known SID display without LDAP hit, LDAP modify payload preserving the rest of the security descriptor, insufficient-rights and constraint-violation result handling, Kerberos and LDAPS session initialization, and parser failure for write without owner.
