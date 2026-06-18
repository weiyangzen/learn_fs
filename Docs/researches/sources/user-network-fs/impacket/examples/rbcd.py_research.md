# sources/user-network-fs/impacket/examples/rbcd.py

## Purpose

`rbcd.py` reads and edits the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute on an Active Directory computer account for resource-based constrained delegation workflows. It supports reading current entries, adding one delegate SID, removing one delegate SID, or flushing the attribute.

## Important APIs, Types, and Functions

`create_empty_sd()` builds a self-relative security descriptor with owner `BUILTIN\Administrators`, an empty DACL, and control flags suitable for the RBCD attribute. `create_allow_ace(sid)` creates an access-allowed ACE with mask `983551` (full-control style mask) for the supplied SID.

`RBCD` owns LDAP session/server objects, the `delegate_to` target, resolved `delegate_from` SID, target DN, and a `ldapdomaindump.domainDumper`. `read()`, `write()`, `remove()`, and `flush()` are the public actions. `get_allowed_to_act()` reads the raw attribute, parses it as `ldaptypes.SR_SECURITY_DESCRIPTOR`, logs entries by resolving SIDs, or creates an empty descriptor when the attribute is missing. `get_user_info()` and `get_sid_info()` perform LDAP lookups by sAMAccountName and objectSid.

## Control Flow

`main()` parses identity, delegation arguments, action, LDAP/LDAPS, and authentication options. It requires `-delegate-to` and additionally requires `-delegate-from` for write. After `parse_identity()` and `init_ldap_session()`, it constructs `RBCD` and dispatches to the requested action. Write and remove both resolve source and target, read the current security descriptor, mutate the DACL in memory, then replace the LDAP attribute.

## State and Persistence Behavior

Read mode is non-mutating. Write mode persists a modified binary security descriptor to `msDS-AllowedToActOnBehalfOfOtherIdentity`. Remove persists a descriptor with matching ACEs removed. Flush persists an empty attribute value by replacing it with an empty list. Local state is transient; no local files are written.

## Dependencies and Integration Points

The script depends on `ldap3`, `ldapdomaindump`, Impacket `ldaptypes`, `init_ldap_session`, and `parse_identity`. It integrates with AD LDAP/LDAPS and requires write access to the target computer object’s RBCD attribute. It expects computer account names to include trailing `$` when appropriate.

## Risks and Edge Cases

The CLI does not require `-delegate-from` for `remove`, so `remove(None)` can reach LDAP lookup with a null account. Replacing the full attribute can overwrite concurrent RBCD changes made between read and write. The full-control mask is broad. Empty or malformed descriptors are replaced with a newly constructed descriptor, which may lose nonstandard ACL metadata. Error handling logs LDAP result messages but does not necessarily fail the process. The script relies on sAMAccountName-only lookup; SID/DN direct inputs are left as a TODO.

## Test Signals

Useful tests include empty descriptor creation binary round-trip, ACE SID encoding, read/write/remove/flush LDAP modify payloads, duplicate SID detection, malformed or absent RBCD attribute handling, missing source/target account errors, LDAPS and Kerberos session initialization, and lab validation that S4U2Proxy works only after the expected ACE is present.
