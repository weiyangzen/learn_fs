# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/smb.c

Main SMB/CIFS command dispatcher for `cifsd`. It handles negotiation, NTLM challenge setup, session setup/logoff, tree connect/disconnect, file open/create/read/write/close, directory creation/removal, rename/delete, metadata query/set, echo, transactions, and transaction2 subcommands.

The implementation maps SMB operations directly to Plan 9 file operations through helpers such as `createfile`, `getfile`, `xdirstat`, `openfind`, `readfind`, `dirwstat`, `pread`, and `pwrite`. It supports Unicode names, large files, NT status responses, NT create, Trans2 query/set path/file/fs information, directory enumeration levels, and CIFS Unix extensions for basic stat fields.

Authentication state is global per process/session: `smbnegotiate` may obtain an NTLM challenge, `smbsessionsetupandx` validates it with Plan 9 auth, changes connection ownership, and sets a hashed session UID. `smbcmd` enforces negotiation order, login completion, and UID checks before dispatch.

Limitations are explicit: many SMB commands return not supported or not implemented, locking is parsed but not actually enforced, and transaction responses are single-buffer responses constrained by the client buffer size.
