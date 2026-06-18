# sources/user-network-fs/samba/source4/torture/unix/whoami.c

## Purpose
`whoami.c` tests the CIFS UNIX extension `SMB_QFS_POSIX_WHOAMI`. It verifies that the server reports the authenticated user's POSIX UID/GID, supplementary groups, SID list, mapping flags, and buffer truncation behavior consistently, optionally cross-checking SIDs against LDAP tokenGroups.

## Important APIs, Types, and Functions
The local `struct smb_whoami` stores mapping flags and mask, server UID/GID, GID and SID counts, SID byte count, reserved field, GID list, and SID list. Core helpers are `connect_to_server()`, `whoami_sid_parse()`, `smb_raw_query_posix_whoami()`, `test_against_ldap()`, and the exported `torture_unix_whoami()`.

## Control Flow
`torture_unix_whoami()` connects to the SMB server with command-line credentials and calls `smb_raw_query_posix_whoami()` with a large buffer. The query helper sends a Trans2 `TRANSACT2_QFSINFO` request with info level `SMB_QFS_POSIX_WHOAMI`, validates the fixed 40-byte response header, parses optional 64-bit GIDs, parses SIDs with `whoami_sid_parse()`, and verifies that counts and byte lengths consume the response exactly.

The main test checks the guest mapping flag if the server advertises `SMB_WHOAMI_GUEST`. If a torture `addc` setting is present, it connects to LDAP and `test_against_ldap()` compares the returned CIFS SID list with `tokenGroups`. On a DC it expects exact ordered equality; on a member server it filters domain SIDs before comparing. The final query uses a small max-data value (`0x40`) and expects the server to omit GID and SID lists while returning valid fixed fields.

## State and Persistence Behavior
The test does not create files. It creates an authenticated SMB session, optionally an LDAP connection, allocates parsed SID/GID arrays under talloc contexts, and disconnects the tree with `smbcli_tdis()` on success or failure.

## Dependencies and Integration Points
It depends on SMB1 raw Trans2 APIs, credentials, loadparm, resolver/event context, dom SID parsing, LDB, Samba DSDB helpers, LDAP wrapping, and UNIX extension constants. It is registered by `unix.c` as `unix.whoami`.

## Risks
The optional LDAP comparison is environment-sensitive: member servers and DCs report different SID sets, ordering assumptions can be brittle, and missing `addc` skips that deeper validation. The SID parser enforces maximum sub-authority count and response length, so malformed server responses fail fast. Small-buffer behavior must match the server's truncation contract.

## Test Signals
Signals include a valid fixed whoami header, zero reserved field, coherent GID/SID counts and byte lengths, guest flag consistency with credentials, optional LDAP tokenGroups alignment, and empty GID/SID lists when queried with the small response buffer.
