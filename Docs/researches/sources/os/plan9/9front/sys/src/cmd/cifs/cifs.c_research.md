# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/cifs.c

Core SMB/CIFS client RPC construction and common file/share operations.

Key behavior:
- `cifsdial` connects to TCP CIFS or falls back to NetBIOS, initializes session state, flags, ids, MTU, signing mode, and Unicode support.
- `cifshdr` allocates a packet, emits NetBIOS and SMB headers, assigns sequence numbers for signing, and fills TID/PID/UID/MID fields.
- `pbytes` finalizes the SMB word-count area and starts the byte-count area.
- `cifsrpc` finalizes byte count, signs if enabled, serializes the request through `nbtrpc`, validates reply size/magic/command, parses status and ids, checks signing/sequence behavior, and maps NT/DOS errors.
- `CIFSnegotiate` offers only `NT LM 0.12`, parses server capabilities, time, timezone, challenge, domain/name strings, and Unicode support.
- `CIFSsession` performs session setup with encrypted or plaintext responses and records guest/remote OS state.
- `CIFStreeconnect`, `CIFSlogoff`, and `CIFStreedisconnect` manage share sessions.
- Provides SMB operations for delete file, delete/create directory, rename, NT create/open, legacy SMB open/create, read, write, flush, close, find-close, echo, and set-information.
- Read/write paths support large file offsets when server capabilities permit.

Dependencies:
- Includes Plan 9 9P/thread headers and `cifs.h`.
- Depends on packet marshaling helpers (`p8`, `pl16`, `ppath`, `gmem`, etc.), NetBIOS transport, auth/signing from `auth.c`, and error mapping functions.

Research notes:
- The code is SMB1-era CIFS, with explicit compatibility handling for old Samba and Win9x/NT families.
- A debug-only bad-MAC path currently prints but does not return failure where marked FIXME.
