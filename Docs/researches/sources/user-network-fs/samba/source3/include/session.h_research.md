# sources/user-network-fs/samba/source3/include/session.h

## Purpose
`session.h` defines the `sessionid` record used to describe currently valid SMB user sessions. These records are claimed during session setup and released when the corresponding VUID/session is destroyed, supporting session tracking, utmp, PAM, and administrative enumeration.

## Important APIs, Types, And Control Flow
`struct sessionid` stores Unix uid/gid, username, hostname, NetBIOS name, remote machine, textual and numeric ids, owning `server_id`, IP string, connection start time, negotiated dialect, authentication flag, encryption flags, cipher, signing mode, signing flags, and a pointer to the `smbXsrv_session_global0` global session record. The header declares no functions; traversal is exposed elsewhere, notably through `sessionid_traverse_read()` in `proto.h`.

## State And Persistence
The structure represents persisted or shared session database entries, commonly backed by sessionid TDB code. It captures security and transport state at login time and links records to the owning smbd process through `server_id`.

## Dependencies And Integration Points
It depends on Samba fixed strings (`fstring`), generated `server_id`, SMB dialect/security types, and smbXsrv session global structures. It integrates with session setup/teardown, PAM/utmp accounting, admin tools that list sessions, encryption/signing reporting, and cleanup for dead server processes.

## Risks And Test Signals
Risks include stale records after abnormal disconnect, fixed-string truncation of host/user names, inconsistent authenticated/encryption/signing reporting, dangling `global` pointers if persisted incorrectly, and cleanup errors when server ids are reused. Test signals include session setup and logoff record creation/deletion, crash cleanup, traversal output, long username/hostname truncation, guest versus authenticated sessions, SMB dialect/encryption/signing metadata, and multi-session-per-process behavior.
