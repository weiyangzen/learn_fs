# sources/user-network-fs/impacket/tests/SMB_RPC/test_smbserver.py

## Purpose

`test_smbserver.py` provides local unit and pseudo-functional coverage for Impacket's embedded SMB server. It checks path normalization and file-jail enforcement, then starts `SimpleSMBServer` on localhost and drives it with Impacket's own `SMBConnection` client for authentication, share browsing, file I/O, directory operations, path traversal blocking, Unicode names, SMB1/SMB2 behavior, and server shutdown.

## Important APIs, Types, and Functions

`StoppableMixin` overrides `serve_forever`, `close_request`, and `get_request` so the test server can exit cleanly from a thread. `SMBSERVERForTests` combines the mixin with `SMBSERVER`. `SMBServerUnitTests` covers `normalize_path` and `isInFileJail`.

`SimpleSMBServerFuncTests` defines the shared server/client fixture. It uses `SimpleSMBServer`, `SMBConnection`, `SessionError`, `compute_lmhash`, `compute_nthash`, `assertRaisesRegex`, `assertCountEqual`, `StringIO`, and `BytesIO`. Subclasses toggle `server_smb2_support` and client preferred dialect: `SimpleSMBServer2FuncTestsClientFallBack` enables SMB2 server support while forcing an SMB1 client dialect, and `SimpleSMBServer2FuncTests` enables SMB2 with default client negotiation and adds directory deletion coverage.

## Control Flow

`setUp()` creates a jail directory, a directory inside the jail, unjailed control paths, normal and Unicode files, and initial content. `tearDown()` removes files/directories and stops the server. `get_smbserver()` adds credentials and a share unless requested otherwise, and applies SMB2 support. `start_smbserver()` runs `server.start()` in a daemon thread due to a Python 3.13 multiprocessing issue. `stop_smbserver()` calls server stop methods, clears `must_serve`, sleeps briefly, and joins the thread.

Functional tests start a fresh server, create a client, assert unauthenticated access failures, authenticate, perform the target operation, assert filesystem results or returned SMB metadata, and close the client. Operations include valid and invalid password/hash login, Unicode username login, share listing, tree connect/disconnect, listing files and patterns, put/get/delete/rename files, create/delete directories, open/close file handles, and query info. Path traversal attempts using `..` are expected to fail with `STATUS_OBJECT_PATH_SYNTAX_BAD` and leave unjailed files untouched.

## State and Persistence Behavior

The tests create and delete real local files/directories in the current working directory (`jail_dir`, `unjailed_file`, and related names) and bind a localhost listener on port 1445. Server state includes credentials, shares, dialect support, connection/thread state, and `must_serve`. The fixture attempts cleanup in `tearDown`, but interrupted or failed runs can leave filesystem artifacts or an occupied port. The SMB2 class changes expected directory listing contents because SMB2 responses omit `.` and `..`.

## Dependencies and Integration Points

The file integrates `impacket.smbserver` with `impacket.smbconnection` through real socket traffic on localhost. It also checks lower-level path helper behavior directly. It depends on `six` for Python 2 compatibility helpers and skip behavior, Python threading/select/socket primitives, and the server classes' ability to accept a custom SMB server class.

## Risks and Edge Cases

Port 1445 conflicts can break the suite. Thread shutdown is timing-sensitive and uses a short sleep before join. Filesystem cleanup assumes directories are empty; a failed intermediate operation can affect later teardown. The jail tests are security-critical: traversal via list, put, get, delete, create directory, rename, open, and SMB2 delete directory must not touch unjailed paths. Unicode filename tests are skipped under Python 2. Some server command families remain listed as TODO, so this suite covers important but not exhaustive SMB server behavior.

## Test Signals

Strong signals are correct auth acceptance/rejection, access-denied responses before login, share listing including `IPC$`, file and directory operation success after login, query-info sizes, Unicode name support, clean local server shutdown, and consistent traversal blocking. Run this file after changes to `smbserver.py`, embedded server threading, path normalization/jail logic, SMB1/SMB2 command handlers, or `SMBConnection` client interoperability.
