# sources/user-network-fs/impacket/impacket/smbserver.py

## Purpose

`smbserver.py` implements Impacket's in-process SMB server stack. It accepts NetBIOS-over-TCP sessions, negotiates SMB1 or SMB2, authenticates users with NTLM and optionally Kerberos/NetLogon-assisted validation, maps tree connections to configured shares, and translates SMB file, directory, transaction, named-pipe, and query/set-info operations into local filesystem and local socket operations.

The file also provides helper RPC servers for `srvsvc` and `wkssvc`, plus `SimpleSMBServer`, a convenience facade that builds a minimal config, registers IPC named pipes, and exposes methods for adding shares, credentials, SMB2 support, Kerberos/NTLM support, callbacks, and challenge/log settings.

## Important APIs, Types, and Functions

- Utility functions:
  - `computeNTLMv2()` verifies NTLMv2 proof strings and derives the exported session key used for signing.
  - `outputToJohnFormat()` and `writeJohnOutputToFile()` format captured NTLM responses and append them to JtR-style dump files.
  - `decodeSMBString()` / `encodeSMBString()` centralize SMB1 Unicode vs ASCII string handling.
  - `normalize_path()` and `isInFileJail()` normalize requested filenames and attempt to keep accesses inside the share root.
  - `openFile()`, `queryFsInformation()`, `findFirst2()`, `queryPathInformation()`, `queryFileInformation()`, and `queryDiskInformation()` are shared filesystem helpers used by both SMB1 and SMB2 handlers.
- SMB1 transaction classes:
  - `TRANSCommands` implements minimal RAP/LANMAN share/server info and named-pipe transaction forwarding.
  - `TRANS2Commands` handles find-first/find-next, filesystem queries, path/file info queries, and path/file info mutation.
  - `NTTRANSCommands` is effectively a default stub.
- `SMBCommands` contains SMB1 command handlers for negotiate, session setup, tree connect/disconnect, open/create, close, read, write, flush, delete, rename, mkdir/rmdir, query information, transactions, lock, echo, logoff, and default not-implemented replies.
- `SMB2Commands` contains SMB2 command handlers for negotiate, session setup, tree connect/disconnect, create, close, query/set info, read/write, flush, query directory, ioctl, lock, cancel, echo, logoff, and default unsupported replies. Internal helpers `_ntlm_auth()`, `_kerberos_auth()`, and `generic_negTokenResp()` build the authentication path.
- `Ioctls` implements `FSCTL_PIPE_TRANSCEIVE`, `FSCTL_VALIDATE_NEGOTIATE_INFO`, and a DFS referrals stub.
- `SMBSERVERHandler` owns one TCP client loop: accepts NetBIOS session requests, receives packets, delegates to `SMBSERVER.processRequest()`, and sends all response packets.
- `SMBSERVER` is the core threaded `socketserver.TCPServer`; it owns configuration, credentials, command dispatch tables, active connection state, named-pipe registration, signing routines, and request/response packet assembly.
- `WKSTServer` and `SRVSServer` are small `DCERPCServer` subclasses backing `wkssvc` and `srvsvc` named pipes.
- `SimpleSMBServer` is the public convenience wrapper around `SMBSERVER`, `SRVSServer`, and `WKSTServer`.
- `NetLogon` establishes an NRPC secure channel and calls `NetrLogonSamLogonWithFlags` to obtain a signing key when computer account credentials are configured.

## Control Flow

Incoming traffic enters `SMBSERVERHandler.handle()`, which wraps the accepted socket in `nmb.NetBIOSTCPSession`. NetBIOS session requests are accepted directly; SMB payloads are passed to `SMBSERVER.processRequest()`.

`processRequest()` first tries to parse SMB1 with `smb.NewSMBPacket`; on failure it parses SMB2 with `smb2.SMB2Packet`. SMB1 requests are rejected before authentication except negotiate and session setup. SMB2 requests are similarly limited to negotiate/session setup before authentication. SMB2 compound requests are walked via `NextCommand`, with each request dispatched independently and later reassembled with 8-byte alignment and optional signing.

SMB1 dispatch is table-driven through `__smbCommands`; transaction commands receive one of the transaction subcommand maps. Most handlers mutate per-connection state, then return response command objects and an NT status. `processRequest()` wraps those commands into SMB1 response packets, fills IDs/status fields, and signs when enabled.

SMB2 dispatch is table-driven through `__smb2Commands`. Handlers usually return SMB2 response structures or `SMB2Error`; `processRequest()` wraps them in `SMB2Packet` responses, copies credit/session/tree/message fields, handles related-operation flags for compounds, and signs responses with HMAC-SHA256 when enabled.

Authentication is SPNEGO/NTLM/Kerberos aware. SMB1 `smbComSessionSetupAndX()` handles extended-security SPNEGO blobs and basic security. SMB2 `smb2SessionSetup()` identifies the mechanism, calls `_ntlm_auth()` or `_kerberos_auth()`, updates `connData`, and returns `STATUS_MORE_PROCESSING_REQUIRED`, success, or failure. NTLM challenge messages are built from configured server name/domain/challenge; successful authentication records parsed authenticate messages, username/domain, session keys, and optional JtR output.

Filesystem operations flow from create/open handlers into local `os.open()` or registered named-pipe sockets. The generated FID/FileID is stored in `connData['OpenedFiles']`; later read/write/query/set/close handlers use that state to operate on the same local descriptor, path, or pipe socket.

## State and Persistence Behavior

Server-wide state lives on `SMBSERVER`:

- `__serverConfig` holds global settings and share sections.
- `__credentials` stores normalized users mapped to `(uid, lmhash, nthash)`.
- `__registeredNamedPipes` maps pipe names to local socket addresses.
- `__smbCommands`, `__smbTransCommands`, `__smbTrans2Commands`, `__smbNTTransCommands`, `__smb2Commands`, and `__smb2Ioctls` are mutable dispatch maps exposed through hook/unregister methods.
- Feature and auth flags include SMB2 support, Kerberos support, NTLM support, anonymous logon, DropSSP, and computer-account credentials.

Per-client state lives in `__activeConnections[connId]`, initialized by `addConnection()` and removed by `removeConnection()`. It tracks packet count, client address, `Uid`, connected tree shares, open files, SMB1 search IDs, SMB2 last request metadata, signing keys/sequence, challenge response material, and authentication state. This state is in memory only and scoped to the handler thread connection.

Persistent external effects are local filesystem operations under configured shares: files/directories are created, renamed, removed, truncated/extended, timestamped, read, written, and flushed. `DeleteOnClose` persists as an in-memory flag until close, then removes the file or directory unless the share is read-only. Authentication captures may be appended to `jtr_dump_path`. Logging may persist through `logging.basicConfig()` if configured with a real log file.

## Dependencies and Integration Points

The module depends heavily on Impacket's SMB, SMB2, NetBIOS, NTLM, SPNEGO, Kerberos ASN.1/crypto, UUID, DCE/RPC transport, EPM, NRPC, SRVS, WKST, and status-code modules. It also uses `pyasn1` for Kerberos/SPNEGO encoding and decoding, `six` for Python compatibility, `socketserver` for threading, and standard `os`, `socket`, `struct`, `hashlib`, `hmac`, `fnmatch`, and `configparser` functionality.

Primary integration points are:

- Config files or generated config sections defining `global`, `IPC$`, and share entries.
- `SimpleSMBServer.addShare()` / `removeShare()` for runtime share management.
- `addCredential()` and `setCredentialsFile()` for NTLM credential validation.
- `setComputerAccount()` / `setComputerAccountCredentials()` for Kerberos and NetLogon paths.
- `registerNamedPipe()` and `unregisterNamedPipe()` for routing IPC pipe traffic to local DCE/RPC servers or user-provided sockets.
- `hookSmbCommand()`, `hookSmb2Command()`, `hookTransaction()`, `hookTransaction2()`, and `hookNTTransaction()` for replacing or extending protocol behavior.
- `setAuthCallback()` for observing completed authentication attempts.

## Risks and Edge Cases

- Path traversal protection is central but fragile. `isInFileJail()` uses `os.path.commonprefix()`, which is string-prefix based and can be unsafe for sibling paths with shared prefixes; callers also vary in how they normalize leading separators and root-relative paths.
- The header TODOs explicitly warn about path traversal, missing locking, inconsistent error handling, partial transaction support gaps, and shared connection-data organization.
- Several operations assume well-formed client data and raise exceptions on malformed offsets, missing fields, unsupported levels, or unexpected authentication blobs.
- There is no global locking around `__activeConnections`, dispatch tables, credentials, registered pipes, or config updates despite threaded request handling.
- SMB signing is implemented, but SMB2 parsing calls `signSMBv2()` on received packets instead of verifying signatures, so request integrity checking is not equivalent to a production server.
- Read-only shares are enforced in many write/create/delete/rename paths, but enforcement is distributed and should be regression-tested for every mutating command, including set-info rename/delete-on-close.
- Some filesystem behavior is intentionally approximate: disk info is fake, allocation info is mostly ignored, oplocks/change notify/security descriptors/quota are unsupported or stubbed, and writes past EOF are skipped rather than extending sparse regions normally.
- Authentication behavior can allow guest/anonymous access when no credentials or permissive config are present; this is intentional for examples but high risk for real deployments.
- JtR hash dumping logs and writes credential material; failures are swallowed broadly.
- The `TRANS2Commands.setPathInformation()` jail check appears inverted: it sets `STATUS_OBJECT_PATH_SYNTAX_BAD` when `isInFileJail(path, fileName)` is true, which likely blocks valid paths and misses the intended error condition.
- `NetLogon.__init__()` uses `random.randbytes(8)` as a default argument, so the default client challenge is generated at import/function-definition time rather than per instance.

## Test Signals

Useful regression coverage should include:

- SMB1 and SMB2 negotiate/session-setup flows for anonymous, guest, configured NTLM credentials, failed credentials, disabled anonymous logon, disabled NTLM, Kerberos-enabled config, and auth callback invocation.
- SMB1/SMB2 tree connect to valid disk shares, `IPC$`, unknown shares, and case variants.
- Path jail tests for `..`, absolute paths, backslash paths, symlink escapes, and sibling-prefix names such as `/tmp/share` vs `/tmp/share_evil`.
- Create/open/read/write/flush/close for files and directories, including read-only shares, overwrite/create dispositions, delete-on-close, EOF reads, writes at and beyond EOF, and Windows directory `VOID_FILE_DESCRIPTOR` behavior where applicable.
- SMB1 transaction2 and SMB2 query-directory pagination, restart/reopen flags, single-entry responses, unsupported info classes, no-match behavior, and search state cleanup.
- Set-info and TRANS2 set-info tests for timestamps, file size extension, deletion, non-empty directory deletion, rename collision, and rename traversal.
- Named-pipe integration tests using `SRVSServer`/`WKSTServer`, `FSCTL_PIPE_TRANSCEIVE`, LANMAN share enumeration, and registered custom pipe sockets.
- Compound SMB2 request tests, including related-operation `0xff...` FileID reuse through `LastRequest`, packet alignment, and signed compound responses.
- Config processing tests for generated `SimpleSMBServer` config, file-based config, credentials file parsing, JtR path, SMB2 support toggling, feature toggles, log-file setup, and computer account settings.
