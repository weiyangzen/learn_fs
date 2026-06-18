# sources/user-network-fs/samba/source4/dsdb/tests/python/token_group.py

## Purpose

`token_group.py` verifies that Samba's constructed token group attributes and group-membership APIs agree with independent token calculations. It compares LDAP `tokenGroups` and `tokenGroupsGlobalAndUniversal`, internally computed `security_token` SIDs, Kerberos PAC SIDs, a manual transitive closure over group membership and primary groups, and SAMR `GetGroupsForUser` results.

## Important APIs, Types, and Functions

The module uses `SamDB`, `samba.auth.user_session()`, `AuthContext`, `gensec.Security`, `ndr_unpack(dom_sid, ...)`, `samba.dcerpc.samr`, and group type constants such as `GTYPE_SECURITY_GLOBAL_GROUP` and `GTYPE_SECURITY_UNIVERSAL_GROUP`. The recursive `closure(vSet, wSet, aSet)` helper expands membership edges. `StaticTokenTest` validates the current command-line user. `DynamicTokenTest` creates a controlled user and nested group graph, then validates token behavior under that graph.

`DynamicTokenTest.filtered_closure()` rebuilds membership edges from LDAP, adds primary-group edges, filters vertices by group type, and expands closure. This models the MS-ADTS/MS-DRSR algorithms used by `tokenGroupsGlobalAndUniversal` and SAMR checks.

## Control Flow

The script requires explicit Kerberos mode rather than `AUTO_USE_KERBEROS`, sets sealing on credentials, normalizes URL after class definitions, and runs Subunit tests. `StaticTokenTest.setUp()` reads rootDSE `tokenGroups`, constructs a `<SID=...>` DN for the user, computes a local session token with flags for default groups, authenticated identity, simple privileges, and NTLM when appropriate, and appends Kerberos-only asserted identity/claims SIDs when needed.

`DynamicTokenTest.setUp()` creates one user and seven groups: direct domain-local, global, and universal groups; a universal chain from global group to universal groups; a domain-local group containing a universal group; and another domain-local direct group. It binds as the test user, discovers the user's SID DN, and computes the session token. Tests compare rootDSE tokenGroups, DN tokenGroups subset behavior, Kerberos PAC groups, manual full tokenGroups closure, filtered global/universal closure, and SAMR output.

## State and Persistence Behavior

Dynamic tests create persistent users and groups under `CN=Users` and remove them in teardown with `delete_force()`. A separate no-member SAMR test creates and deletes `tokengroups_user2` inside the test. Group nesting is real AD state, so failures before teardown can leave objects that collide with later runs. Static tests do not create state but depend on the credentials used to run the test.

## Dependencies and Integration Points

The file covers LDAP constructed attributes, auth session construction, NTLM/Kerberos SID differences, GENSEC client/server Kerberos exchange, PAC parsing through `session_info()`, SAMR RPC over sealed `ncacn_ip_tcp`, primary group lookup, group type filtering, and SID-to-DN LDAP resolution. It depends on command-line credentials, machine credentials for the GENSEC server side, and an LDAP URL for rootDSE and SAMR host discovery.

## Risks and Edge Cases

Kerberos and NTLM add different extra SIDs, so expected missing sets must track authentication mode. Some tests call `self.fail()` when URL is not LDAP rather than skipping. `closure()` is recursive and mutates sets in place; it is fine for these small graphs but not cycle-optimized for arbitrary large domains. In `test_samr_GetGroupsForUser`, the condition after `res3 = ...` checks `len(res)` instead of `len(res3)`, which looks like a typo and can mask filtering mistakes. The manual algorithms depend on `memberOf` visibility and correct primaryGroupID SID resolution.

## Test Signals

Pass signals include exact rootDSE tokenGroups equality with internal session SIDs, DN tokenGroups being the expected subset of full token SIDs, Kerberos PAC SIDs matching internal token SIDs, manual closure matching LDAP constructed attributes, global/universal filtering matching `tokenGroupsGlobalAndUniversal`, SAMR returning the primary group plus expected global/universal memberships with default attributes, and a no-member user returning only the primary group.
