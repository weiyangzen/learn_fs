# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ftpfs/proto.c

Core FTP protocol adapter for `ftpfs`. It opens the control connection, handles optional FTP-over-TLS setup, authenticates interactively or through auth keys, detects the remote OS, and initializes the mirrored remote root/current directory model.

The file implements active/passive data connections, FTP commands for listing, reading, writing, creating, and removing files/directories, and protocol reply parsing. Directory listing parsing covers Unix/Plan 9, Windows NT, VMS, VM, TOPS, NetWare, TSO/MVS-like formats, with path builders for Unix, VMS, and MVS remote names.

It also owns transfer type switching, keepalive, password input with console raw mode, Latin-1-to-UTF conversion for foreign listings, and helpers for safely reallocating `Dir` structures used by the local 9P mirror.
