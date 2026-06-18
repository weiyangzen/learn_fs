# sources/user-network-fs/impacket/impacket/acl.py

## Purpose

`acl.py` implements Windows file ACL inspection and mutation over SMB. It parses NTFS security descriptor pieces, translates SIDs through LSARPC, renders DACL ACEs in an icacls-like short form, and provides `SMBFileACL` methods to read, grant, revoke, or delete permissions on remote SMB files.

## Important APIs, Types, and Functions

Constants define ACE inheritance flags and a limited supported permission map: `R`, `W`, `D`, `X`, and `F`. `FileNTUser` models a DACL header, `ACL_SID` models SIDs and supports string conversion plus `build_from_string`, and `FileNTACE` models access-allowed ACE records with readable flag/right rendering helpers.

`SecurityAttributes` is a container for owner, group, raw DACLs, and readable DACL strings. `SMBFileACL` is the main operational class. Important methods include connection lifecycle (`close_connection`, `close_file`, `open_file`), LSARPC setup (`start_dce_rpc`, `open_policy_handle`), SID/name translation (`set_sid_to_name`, `sids_to_names`, `name_to_sid`), ACE construction (`permissions_to_ace`), descriptor parsing (`get_security_attributes`, `get_permissions`), DACL mutation (`insert_permission`), and remote write-back (`set_permissions`).

## Control Flow

Constructing `SMBFileACL` either reuses an existing `SMBConnection` or creates and authenticates one with NTLM or Kerberos. It then starts an SMB-backed LSARPC transport, binds LSAD, and opens a policy handle for name/SID lookup. `get_permissions` opens the target file with `READ_CONTROL`, queries security information through the underlying SMB connection, parses `FileSecInformation`, resolves owner/group and ACE SIDs, then closes the file handles in a `finally` block.

`set_permissions` opens the file with `GENERIC_ALL`, resolves the target user to a SID, converts requested permission letters to an ACE, queries the current descriptor, calls `insert_permission`, and writes the modified DACL back through `setInfo` with DACL security information. `insert_permission` walks the existing ACE buffer, matches by SID, ORs rights for grants, clears rights for revokes, removes zero-right ACEs or delete requests, and inserts a new ACE at the front only for new grant entries.

## State and Persistence Behavior

The class holds live SMB and DCE/RPC connection state (`connection`, `transport`, `dce_rpc`, `policy_handle`, `tid`, `fid`) plus SID/name caches. Remote persistence happens only when `set_permissions` successfully calls SMB `setInfo`; otherwise changes are local byte-buffer transformations. `close_file` and `close_connection` are responsible for releasing remote handles, trees, transports, and owned SMB connections.

## Dependencies and Integration Points

The module depends on `impacket.structure.Structure`, `lsad`, `lsat`, `SMBTransport`, `SMBConnection`, and SMB3 file/security constants. It integrates tightly with `FileSecInformation` layout from `smb3structs` and with LSA lookup calls over the `lsarpc` named pipe. It is meant for SMB file permission workflows and likely consumed by tools that need icacls-like remote ACL operations.

## Risks and Edge Cases

Security descriptor parsing assumes owner, group, and DACL offsets are ordered and present. `ACL_SID.build_from_string` names the SID authority field `numAuth`, which is the identifier authority, not the subauthority count; malformed SID strings can produce invalid binary SIDs. `FileNTACE.__str__` covers only a subset of rights. `insert_permission` decrements ACE count by one even if multiple matching ACEs were deleted, and it tracks ACEs in a dictionary by SID, so duplicate ACEs collapse during readable parsing. `name_to_sid` wraps all failures in a generic exception. The module uses private `_SMBConnection` APIs, which are more fragile than public wrappers.

## Test Signals

Unit tests should cover SID string/binary round-trips, ACE rights rendering, permission letter parsing, grant/revoke/delete mutations on synthetic security descriptors, ACE count/size updates, and duplicate ACE behavior. Integration tests need a controlled SMB server or mocked `SMBConnection`/LSA RPC path to verify `queryInfo`, `setInfo`, handle cleanup, and SID lookup fallback behavior.
