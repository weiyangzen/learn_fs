# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ftpd.c

Plan 9 FTP server with optional explicit/implicit TLS, active/passive data channels, anonymous modes, Plan 9 auth login, per-user namespace selection, and command dispatch.

Commands cover authentication/TLS (`AUTH`, `PBSZ`, `PROT`), login (`USER`, `PASS`), navigation, listing (`LIST`, `NLST`, `MLSD`, `MLST`), file transfer (`RETR`, `STOR`, `REST`), directory/file mutation, rename, passive/active data setup, and session termination. Long operations may be forked through `asproc`.

It binds the client connection network into `/net` while opening data channels, supports TLS on the data channel, and uses Plan 9 file APIs for all filesystem access. Anonymous `none` users are restricted from delete/mkdir/rename/store-style mutations by command checks.
