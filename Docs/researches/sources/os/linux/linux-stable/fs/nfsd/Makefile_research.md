# File Research: sources/os/linux/linux-stable/fs/nfsd/Makefile

Purpose: Builds the NFSD module and optional feature objects.

Key responsibilities:
- Adds local include path for trace events.
- Builds core `nfsd.o` from service, control, filehandle, VFS, export, auth, lockd, duplicate reply cache, stats, filecache, NFSv3, and netlink objects.
- Ensures `trace.o` is compiled first.
- Adds objects for NFSv2, ACL extensions, NFSv4, pNFS layouts, localio, and debugfs based on configs.
- Provides `xdrgen` phony target for regenerating checked-in NFSv4 XDR code from documentation XDR definitions.

Integration:
- Mirrors Kconfig feature selection.
- Ties generated NFSv4 XDR files to `tools/net/sunrpc/xdrgen`.

Risks and notes:
- Normal builds use checked-in generated XDR code; regeneration is developer-only.
