# File Research: sources/os/bsd/netbsd-src/lib/libquota/Makefile

This Makefile builds the NetBSD `libquota` library. It sets `WARNS?=5`, names the library `quota`, and links against `librpcsvc`, which is needed by the NFS rquota backend.

The source list includes the public handle/open/schema/get/put/delete/cursor layers plus the three backend implementations: NFS RPC, old quota files, and kernel quotactl. The installed manual page is `libquota.3`, with many MLINKS for individual public functions such as `quota_open`, `quota_get`, `quota_put`, `quota_delete`, cursor operations, schema inspection, quota on/off, and `quotaval_clear`.

It includes `<bsd.own.mk>` and `<bsd.lib.mk>`, following the normal NetBSD library build pattern.
