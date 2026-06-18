# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/apinums.h

Header of LAN Manager / RAP API numeric identifiers. It maps remote administration APIs such as share, session, file, server, group, user, workstation, print, DFS, and account operations to stable integer call numbers.

Used by `trans.c` to construct `\\PIPE\\LANMAN` transaction requests. The file is data-only; no logic. `MAX_API` is `215`.
