## sources/user-network-fs/go-fuse/fuse/direntry_freebsd.go

Purpose: FreeBSD-specific raw directory entry layout support.

Important APIs/types/functions: defines platform `dirent` fields and `nameLength`.

Control flow: selected at build time for FreeBSD and used by `DirEntry.Parse`.

State and persistence: none.

Dependencies and integration: supports directory parsing in tests and loopback directory streams on FreeBSD.

Risks and test signals: incorrect struct layout affects every parsed directory entry on FreeBSD.
