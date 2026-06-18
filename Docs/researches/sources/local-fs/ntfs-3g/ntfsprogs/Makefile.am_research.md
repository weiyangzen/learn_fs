# File Research: sources/local-fs/ntfs-3g/ntfsprogs/Makefile.am

Automake rules for building NTFS-3G command-line tools. It supports normal libtool linkage against `libntfs-3g.la` and `REALLYSTATIC` linkage against the static library plus `NTFSPROGS_STATIC_LIBS`, with a compatibility `LINK` workaround for older automake.

When `ENABLE_NTFSPROGS` is set, installed programs include `ntfsfix`, `ntfsinfo`, `ntfscluster`, `ntfsls`, `ntfscat`, `ntfscmp`, `mkntfs`, `ntfslabel`, `ntfsundelete`, `ntfsresize`, `ntfsclone`, and `ntfscp`. Extra tools include `ntfswipe`, `ntfstruncate`, `ntfsrecover`, `ntfsusermap`, `ntfssecaudit`, optionally `ntfsdecrypt`, and quarantined tools such as `ntfsdump_logfile`, `ntfsmftalloc`, `ntfsmove`, `ntfsck`, and `ntfsfallocate`.

The file assigns source lists, `LDADD`, and `LDFLAGS` for each program. `mkntfs` uses `attrdef.c`, `boot.c`, `sd.c`, `mkntfs.c`, and utility files; `ntfscluster` uses `cluster.c`; list-based tools include `list.h`. Crypto builds add GnuTLS/libgcrypt flags for `ntfsdecrypt`.

It also defines `strip`, `libs`, `extra`, and `extras` targets. When mount-helper support is enabled, install hooks create `mkfs.ntfs` and `mkfs.ntfs.8` symlinks to `mkntfs` and its manpage; uninstall hooks remove them.

Dependencies are the top-level libntfs build, generated configuration conditionals, optional crypto libraries, manpage generation, and automake install hooks. The build topology makes `libntfs-3g` the shared implementation dependency for nearly all ntfsprogs.
