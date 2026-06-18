# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/cifs.c

Core SMB1/CIFS protocol client. `cifsdial` tries direct TCP CIFS first, then NetBIOS-over-TCP fallback. `cifshdr`, `pbytes`, and `cifsrpc` build SMB packets, apply signing when enabled, serialize RPC access, validate magic, parse returned IDs/status, and translate NT/DOS errors.

Implements negotiate, session setup, tree connect/disconnect, logoff, file/directory create/delete/rename, NT and legacy open/create, read/write-andX, flush, close, find-close, echo, and basic set-info. It negotiates only `NT LM 0.12`, tracks server capabilities, challenge, timezone, MTU, UID/TID, and optional Unicode/large-file support.

This file is the protocol bridge used by the 9P filesystem in `main.c` and higher-level transaction helpers.
