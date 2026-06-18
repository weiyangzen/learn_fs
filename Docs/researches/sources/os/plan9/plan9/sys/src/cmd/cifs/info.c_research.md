# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/info.c

Defines the virtual info-file directory entries: `Users`, `Groups`, `Shares`, `Connection`, `Sessions`, `Dfsroot`, `Dfscache`, `Domains`, `Openfiles`, `Workstations`, and `Filetable`.

Provides lookup (`walkinfo`), count (`numinfo`), directory synthesis (`dirgeninfo`), lazy content generation (`makeinfo`), reads from cached generated buffers (`readinfo`), and cleanup (`freeinfo`). It uses `mkqid` to align info files with the 9P namespace.
