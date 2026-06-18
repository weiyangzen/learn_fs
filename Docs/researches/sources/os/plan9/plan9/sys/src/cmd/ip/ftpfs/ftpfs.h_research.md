# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ftpfs/ftpfs.h

`ftpfs.h` defines shared structures and APIs for the FTP-backed 9P filesystem.

Key contents:
- Declares opaque `File`, tree `Node`, and remote OS descriptor `OS`.
- `Node` mirrors the remote directory tree with remote name, Plan 9 `Dir`, parent/sibling/child links, cache pointer, depth, open count, and directory-type uncertainty.
- Enumerates remote OS kinds: Unix, Tops, Plan9, VM, VMS, MVS, NetWare, OS/2, TSO, NT, Unknown.
- Declares temp-file cache API, FTP protocol API, and miscellaneous tree/cache helpers.
- Exposes globals such as `remdir`, `remroot`, `os`, `debug`, `usenlst`, `nosuchfile`, `ext`, `defos`, `quiet`, `user`, and `net`.
- Defines cache/validity macros using fields in `Dir`.

Important dependencies:
- Included by `ftpfs.c`, `file.c`, and protocol implementation files outside this group.

Notable risks/quirks:
- Cache and validity state are encoded into `Dir.type`, `Dir.atime`, and `Dir.dev`, which are normally filesystem metadata fields.
