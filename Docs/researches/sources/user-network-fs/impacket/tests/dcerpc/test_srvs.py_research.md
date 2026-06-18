# sources/user-network-fs/impacket/tests/dcerpc/test_srvs.py

## Purpose
This file is a remote integration suite for the Server Service RPC interface (`srvsvc`). It validates Impacket request classes and helper wrappers for connection, file, session, share, server information, transport, file security, path/name canonicalization, DFS, server alias, and share deletion operations.

## Important APIs, Types, and Functions
`SRVSTests` binds `srvs.MSRPC_UUID_SRVS` on `\\PIPE\\srvsvc` with authentication. It uses low-level request classes such as `NetrShareEnum`, `NetrShareAdd`, `NetrServerGetInfo`, `NetrpGetFileSecurity`, and `NetprPathCanonicalize`, plus helper wrappers such as `hNetrShareEnum`, `hNetrServerDiskEnum`, and `hNetprNameValidate`. Data structures include share info levels 0/1/2/501/502/503, `SERVER_ALIAS_INFO_0`, security descriptor buffers, `NULL`, and `OWNER_SECURITY_INFORMATION`.

## Control Flow
Each test connects, builds a request for one or more information levels, sends it, and dumps responses. Paired raw/helper tests mirror the same API coverage. Many enum and get-info calls switch union tags and levels in-place to verify multiple discriminated-union layouts. Share lifecycle tests add `BETUSHARE`, delete it directly, delete it through start/commit, or delete it with `NetrShareDelEx`. File/session tests first enumerate then act on the first returned entry.

## State and Persistence Behavior
The file can modify real server state: temporary shares are created/deleted, IPC$ share remarks are edited then restored, sessions or open files may be closed, server aliases are added/deleted, and file security may be read and written back on `C$\\Windows`. DFS calls mostly expect unsupported or bad-stub responses but still target server configuration APIs. Some disabled `tes_` and `ttt_` methods are intentionally not discovered by unittest.

## Dependencies and Integration Points
Dependencies include `impacket.dcerpc.v5.srvs`, shared DCE/RPC harness configuration, the target machine name, administrative shares (`IPC$`, `C$`), Windows server service behavior, and filesystem/security state on the target. It exposes both NDR and NDR64 SMB transport subclasses via `pytest.mark.remote`.

## Risks
The suite assumes returned enum buffers are non-empty and that built-in shares and files exist, which can fail on hardened or idle systems. Tests may close their own pipe/session, acknowledged by accepted `STATUS_PIPE_BROKEN`, `STATUS_FILE_CLOSED`, and invalid-handle errors. Several cleanup paths are not protected by `finally`, so failed share or alias tests can leave `BETUSHARE` or `BETOALIAS`. String comparisons for unsupported DFS/alias behavior are brittle, and mutating IPC$ remarks or file security on system paths is high impact.

## Test Signals
Signals include successful marshalling of many info-level unions, expected DFS and alias unsupported errors, expected `ERROR_MORE_DATA`/status variants in close/delete paths, restoration of share remarks, add/delete lifecycle success for shares and aliases, and successful round trip of security descriptor data. The misspelled `tes_` and `ttt_` methods are visible coverage candidates but not active tests.
