# sources/user-network-fs/impacket/tests/SMB_RPC/test_acl.py

## Purpose

`test_acl.py` validates Impacket's Windows file ACL management helpers over SMB at the unit level. It uses mocks for network-bound SMB/LSA interactions and byte fixtures for security descriptors, ACEs, and SIDs.

## Important APIs, Types, And Functions

The file imports `unittest`, `mock`, `MagicMock`, `patch`, `SMBFileACL`, `FileNTACE`, `ACL_SID`, `FileNTUser`, `SecurityAttributes`, `SUPPORTED_PERMISSIONS`, and `FileSecInformation`. `TestSMBFileACL.get_mock_smb_file_acl()` creates an `SMBFileACL` with patched `SMBConnection` and `SMBTransport`. Tests cover `name_to_sid()`, `permissions_to_ace()`, invalid permission handling, `SMBFileACL.insert_permission()` grant/revoke/delete behavior, and ACL structure formatting. `TestACLStructures` covers SID representation/build/equality, ACE flag and permission display, and `SecurityAttributes.__str__()`.

## Control Flow

Name resolution patches `lsat.hLsarLookupNames3()` to return a mock SID and asserts stripped SID length. Permission conversion patches `name_to_sid()` and checks the produced `FileNTACE`. Insert-permission tests parse fixed security descriptor blobs, build grant/revoke/delete ACEs, call `SMBFileACL.insert_permission()`, then parse the resulting DACL and assert ACE count changes or preservation. Structure tests instantiate SIDs and ACEs from bytes or strings and inspect equality, hashing, and display output.

## State And Persistence Behavior

The tests avoid real SMB servers by patching connection classes. State is local mocks, byte buffers, and parsed structures. There is no persistence.

## Dependencies And Integration Points

The file exercises `impacket.acl`, `impacket.smb3structs.FileSecInformation`, LSAT name lookup through mocks, and Python `unittest.mock`. It protects ACL behavior used by callers that read or update Windows file permissions.

## Risks And Edge Cases

Two intended close-on-error tests are indented inside `test_insert_permission_grant_new_ace()` after an assertion, making them local functions rather than discovered test methods. Therefore file-handle cleanup on permission-resolution/query errors is not actually tested. Most descriptor mutation tests assert ACE counts, not full binary descriptor integrity or exact rights. Real SMB open/query/set behavior and server-side ACL canonicalization are mocked out. A comment notes a known authority encoding issue in `ACL_SID.build_from_string()`.

## Test Signals

Passing discovered tests signal stable mocked SID lookup, permission string conversion, ACE insertion/merge/removal counts, SID equality/hash, ACE flag formatting, and security attribute display. The nested cleanup tests should be lifted to class scope for resource-cleanup coverage.
