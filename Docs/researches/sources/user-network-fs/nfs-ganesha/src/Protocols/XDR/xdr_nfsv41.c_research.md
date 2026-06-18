# sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nfsv41.c

Purpose: placeholder compilation unit for NFSv4.1 XDR routines with external linkage. The file documents that most Ganesha NFSv4.1 XDR routines are inline definitions in `nfsv41.h`.

Important APIs and types: includes `config.h` and `nfsv41.h`; it does not define callable routines in the current source.

Control flow: no runtime control flow. The unit exists to provide a stable file for non-inline decoder routines if needed and to keep the build list aligned with protocol organization.

State and persistence: none.

Dependencies and integration points: participates in the `nfs_mnt_xdr` object library. Its main integration value is ensuring NFSv4.1 XDR headers compile in this target and leaving a place for future external XDR symbols.

Risks: because most behavior is in headers, changes to `nfsv41.h` can affect many translation units without this file changing. Test and coverage tools may show this file as empty even though it represents an important build edge.

Test signals: build coverage is the main signal. Full NFSv4.1 XDR behavior should be tested through the inline routines and protocol compound encode/decode paths, not through this file directly.
