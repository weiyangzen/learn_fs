# sources/user-network-fs/impacket/tests/SMB_RPC/test_smb.py

## Purpose

`test_smb.py` is a remote SMB client integration suite plus one local regression test. It validates `SMBConnection` behavior across SMB1, NetBIOS-session SMB1, SMB1 Unicode flags, SMB 2.0.2, SMB 2.1, and SMB 3.0 dialect preferences.

## Important APIs, Types, and Functions

`SMBTests(RemoteTestCase)` provides shared remote test methods and `create_connection()`. Concrete classes set `self.dialects`, `self.sessPort`, share/file/directory names, upload file, SMB1 flags, and AES-key transport configuration. The tests exercise `SMBConnection` APIs for negotiation, login, Kerberos login, reconnect, connect/disconnect tree, list path, create/open/close/delete/rename files, read/write, create/delete directories, metadata getters, upload/download callbacks, list shares, session key retrieval, and `queryInfo`.

The local `Test_Issue2099_SessionError_On_Truncated_Response` uses `unittest.mock` to patch `impacket.nmb.NetBIOSTCPSession` and `SMBSessionSetupAndX_Extended_Response_Data.fromString`, constructing minimal SMB negotiate and session-setup responses to assert parse errors become `SessionError`.

## Control Flow

Remote tests create a connection using manual negotiation for SMB1 and direct preferred dialects for SMB2/3. Each test logs in with password, hashes, Kerberos hashes, Kerberos password, or AES as appropriate, performs an SMB operation against the configured administrative share, asserts returned credentials or metadata when applicable, and logs off or closes the connection. File I/O tests create remote files, write 65,535 bytes, read until complete, rename/delete, upload a local `impacket/nt_errors.py`, download to a temporary file, and delete remote artifacts.

The truncated-response regression builds a fake session that returns a valid negotiate packet and a session setup packet whose data parser is forced to raise either `ValueError` or `struct.error`. It asserts `SMBConnection(...).login(...)` raises Impacket's `SessionError` variants rather than exposing raw parser exceptions.

## State and Persistence Behavior

Remote tests mutate the configured share by creating files and directories such as `/TEST` and `/BETO`, then deleting them. They open sockets and explicitly test socket closure with `select`. Reconnect tests preserve stored credentials across logoff/reconnect. The upload/download test creates and deletes a local `impacket/nt_errors.py2` file. The local regression test uses in-memory packet bytes and mocks only, with no network or filesystem dependency.

## Dependencies and Integration Points

The file depends on `RemoteTestCase`, optional `pytest.mark.remote`, `SMBConnection`, `SessionError`, `impacket.smbconnection.smb`, SMB2 dialect constants, `nt_errors`, and `nmb` session ports. It is a broad integration point for SMB negotiation, authentication, file APIs, tree handling, dialect-specific behavior, NetBIOS transport, and error translation.

## Risks and Edge Cases

The remote matrix is sensitive to target OS and dialect support; the file notes Windows 8 limitations when switching SMB2/3 dialects against one machine. Tests operate on administrative shares and require cleanup to avoid stale files. Some methods assume the configured share is writable and that `impacket/nt_errors.py` exists relative to the test working directory. `test_manualNego` calls negotiation on a connection that may already be manually negotiated for SMB1, which makes dialect state important. The local regression protects against malformed server responses producing raw parser exceptions in authentication paths.

## Test Signals

Passing remote tests signal working SMB connection lifecycle, auth variants, dialect selection, file/directory operations, metadata, reconnect credential persistence, and socket closure. The local regression is a targeted signal for issue 2099: truncated session setup responses must raise `SessionError`. Run this file after changes to `smbconnection.py`, `smb.py`, SMB2/3 dialect negotiation, NetBIOS session handling, or file operation wrappers.
