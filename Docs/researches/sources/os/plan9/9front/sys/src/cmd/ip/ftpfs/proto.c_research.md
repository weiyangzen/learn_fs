# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ftpfs/proto.c

FTP protocol engine for `ftpfs`. Handles control connection setup, optional TLS, user/password login via auth or supplied anonymous credentials, remote OS detection, preamble/root selection, type switching, active/passive data connections, request/reply parsing, and keepalives.

Directory parsing is broad: Unix, Plan 9, TOPS, VM, VMS, MVS, NetWare, OS/2, TSO, NT-like listings, and NLST fallback. It converts remote listings into Plan 9 `Dir` records, handles Latin-1-to-UTF conversion, symbolic-link directory probing, and OS-specific path rendering.

File and directory operations map to FTP commands: `LIST`/`NLST`, `CWD`, `RETR`, `STOR`, `MKD`, `DELE`, `RMD`, `QUIT`, `PASV`, and `PORT`. Passive mode is preferred, with active fallback.
