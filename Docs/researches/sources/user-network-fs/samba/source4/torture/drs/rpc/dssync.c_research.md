# sources/user-network-fs/samba/source4/torture/drs/rpc/dssync.c

## Purpose
`dssync.c` is a C torture suite for DRSUAPI `DsGetNCChanges` and `DsGetNT4ChangeLog`. It binds as administrator and as a simulated new DC, fetches naming contexts over DRS, converts replicated objects into DSDB/LDB form, and compares them against LDAP reads of the same objects.

## Important APIs, Types, And Functions
- `struct DsSyncTest` stores DRS bindings, LDAP context, naming-context DNs, old/new DC metadata, and credentials.
- `test_create_context()` parses the binding, enables sign/seal, resolves the server, initializes bind-info extension sets, and creates LDAP URL state.
- `_test_DsBind()` handles DRS bind, peer bind-info normalization across lengths 24/28/32/48/52, and policy handles.
- `test_LDAPBind()` creates an LDB connection with Samba handlers and paged searches.
- `test_analyse_objects()` loads schema from the DRS prefix map, converts replicated objects with `dsdb_replicated_objects_convert()`, fetches corresponding LDAP objects with show-deleted and extended-DN controls, normalizes messages, and compares differences.
- `test_GetNCChanges()`, `test_FetchData()`, and `test_FetchNT4Data()` implement the replication and NT4 changelog tests.

## Control Flow
The fixture creates context, binds admin DRS, binds LDAP, discovers domain/config/schema DNs, and binds as the simulated new DC. `test_FetchData()` selects either a configured partition or domain/config/schema and calls `test_GetNCChanges()` for each. `test_GetNCChanges()` builds level-5 or level-8 requests, applies compression/writeable-neighbor parameters, loops while `more_data` is true, accepts plain or compressed level-1/6 replies, updates high-watermarks, and analyzes each chunk. Optional password-blob logging decrypts and dumps selected secret attributes using the DCE/RPC auth session key. `test_FetchNT4Data()` loops `DsGetNT4ChangeLog` restart cookies and skips unsupported server roles/procnums.

## State And Persistence Behavior
The suite is mostly read-only against the target directory but maintains local high-watermark and restart-cookie state during fetches. If configured with `dssync:save_pwd_blobs_dir`, it writes secret blob files for inspected attributes. It opens DRS policy handles and unbinds both admin and new-DC handles in teardown.

## Dependencies And Integration Points
It integrates generated DRSUAPI NDR clients, DRS blob decoders, DCE/RPC auth, GENSEC session keys, LDB, DSDB schema conversion, LDAP extended controls, CLDAP/name resolution, and Samba torture fixtures. It is an important bridge test between raw DRS replication data and LDAP-visible directory state.

## Risks
LDAP and DRS are not byte-identical transports, so the comparison has explicit skips for secret attributes and `nTSecurityDescriptor` on Deleted Objects. Difference handling warns for certain forward-link mismatches because linked attributes may arrive separately. Optional secret dumping is sensitive and must be controlled. The test depends on server extension support, compression settings, and naming-context size.

## Test Signals
Signals include successful signed/sealed DRS binds, successful LDAP bind, successful schema load from remote prefix map, no unexpected DRS-vs-LDAP message differences, correct handling of compressed replies, high-watermark progress until `more_data` clears, supported or correctly skipped NT4 changelog behavior, and clean DRS unbinds.
