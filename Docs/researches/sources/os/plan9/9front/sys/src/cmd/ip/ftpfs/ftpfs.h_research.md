# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ftpfs/ftpfs.h

Shared declarations for `ftpfs`. Defines the mirrored remote tree `Node`, supported remote OS enum, `OS` name table type, cache/protocol/misc function prototypes, global state, and cache validity macros.

Important state flags include cached/valid qid fields, directory `chdirunknown`, symlink mode bit `DMSYML`, cache timeout, remote root/current directory, remote OS, debug/quiet flags, `usenlst`, and network path.
