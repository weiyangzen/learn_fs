# sources/user-network-fs/samba/source4/dsdb/tests/python/dirsync.py

Purpose: this is the primary DirSync LDAP control regression suite for Samba AD, covering access rights, cookies, naming-context behavior, attribute filtering, deleted objects, linked attributes, extended DN formatting, confidential attributes, and RODC-filtered attributes.

Important APIs/types/functions: `DirsyncBaseTests` creates admin, simple, dirsync, and admin users, grants `GUID_DRS_GET_CHANGES`, and opens sealed no-Kerberos user connections. `SimpleDirsyncTests` covers normal DirSync behavior, errors, attributes, deltas, linked attributes, range retrieval, cookies, deleted items, and `extended_dn`. `SpecialDirsyncTests` mutates schema flags and provides shared confidential/filtered setup. `ConfidentialDirsyncTests`, `FilteredDirsyncTests`, and `ConfidentialFilteredDirsyncTests` assert visibility/empty-element behavior for `SEARCH_FLAG_CONFIDENTIAL`, `SEARCH_FLAG_RODC_ATTRIBUTE`, and both combined.

Control flow: setup builds a dedicated OU and test users, stores base/config DNs, grants DRS rights, and registers cleanup. Simple tests execute DirSync searches with controls such as `dirsync:1:0:1`, `dirsync:1:1:1`, large page sizes, incrementally updated cookie strings, and the linked-attribute flag `2147483648`. Special tests set schema `searchFlags`, add a confidential value, then compare normal LDAP, object-security DirSync, and GET_CHANGES DirSync outcomes.

State and persistence behavior: the suite mutates OUs, group membership, DACLs on the domain base, schema flags, and deleted objects. Cleanup tree-deletes OUs, removes DACL ACEs, and restores searchFlags for special tests. DirSync cookies are parsed and repacked with NDR/base64 for one compatibility case.

Dependencies and integration points: integrates with LDB controls, `SamDB`, `sd_utils`, DRSUAPI security GUIDs, `drsblobs.ldapControlDirSyncCookie`, `ndr_pack`/`ndr_unpack`, `delete_force`, and Samba's credential/test harness.

Risks: high global impact if cleanup fails, especially schema flags and domain DACL changes. Tests assume Windows-compatible DirSync edge semantics, including insufficient-access and unwilling-to-perform distinctions. Some assertions accept either missing or empty attributes unless `insist_on_empty_element` is requested, reflecting backend compatibility needs.

Test signals: exact LDB errors, required operational attributes (`objectGUID`, `parentGUID`, `instanceType`, `nTSecurityDescriptor`), empty deltas from reused cookies, deleted-object visibility, linked attribute range names, extended DN byte formats, and confidential/filtered attribute suppression or visibility under the correct rights.
