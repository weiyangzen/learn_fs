# sources/user-network-fs/impacket/examples/sambaPipe.py

## Purpose

`sambaPipe.py` is an exploit helper for CVE-2017-7494. It authenticates to a Samba SMB server, finds a writable share, uploads a user-supplied shared object, and attempts to trigger loading through a crafted path opened on `IPC$`.

## Important APIs, Types, and Functions

`PIPEDREAM` owns the SMB client and CLI options. `isShareWritable()` probes share write access. `findSuitableShare()` uses SRVSVC `NetrShareEnum` level 2 to find writable shares and their server-side paths. `uploadSoFile()` uploads the local `-so` file. `create()` manually builds an SMB2 CREATE packet. `openPipe()` builds the absolute share path and sends either SMB1 `NT_CREATE_ANDX` or SMB2 CREATE without Impacket's normal NT path conversion. `run()` orchestrates find/upload/trigger/delete.

## Control Flow

The CLI parses target, required `-so`, auth, Kerberos/AES, target IP, DC IP, and SMB port. It logs in with NTLM or Kerberos, disables SMB3 encryption by clearing `SMB2_SESSION_FLAG_ENCRYPT_DATA` when using SMB2/3, then runs `PIPEDREAM`. The exploit path enumerates shares, chooses the first writable one, uploads the shared object, opens `IPC$` with a path pointing at the uploaded object, handles expected `STATUS_OBJECT_NAME_NOT_FOUND`, and deletes the uploaded file in `finally`.

## State and Persistence Behavior

The tool writes the supplied `.so` to a remote writable share and deletes it afterward. If deletion fails or the process is interrupted, the library remains. It may execute code inside vulnerable Samba. It also mutates the in-memory SMB session flags to disable encryption.

## Dependencies and Integration Points

It integrates with `SMBConnection`, low-level SMB1/SMB2 packet classes, SRVSVC over DCE/RPC, Kerberos/NTLM auth, and Samba share path semantics. It relies on Samba exposing Windows-style share metadata and on CVE-2017-7494 behavior.

## Risks and Edge Cases

This is exploit code and can run arbitrary code on vulnerable targets. Writable share detection opens the share root with write access and may miss shares with path-specific permissions. The first writable share may not be suitable. Disabling SMB3 encryption is intrusive and uses private connection internals. `create()` returns only on success and otherwise implicitly returns `None`. Cleanup only removes the uploaded filename from the selected share.

## Test Signals

Unit tests can mock SRVSVC share enumeration, writable probes, upload/delete calls, SMB1/SMB2 dialect selection, and path construction. Integration testing should be restricted to a lab Samba version and should verify cleanup on expected and unexpected trigger errors.
