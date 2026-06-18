# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/sundries.c

Utility routines shared by the OCFS2 mount helper.

It provides checked string duplication/concatenation helpers, quiet-aware error printing, broad signal blocking/unblocking, filesystem type matching, mount option matching with `no*` semantics, path canonicalization, and device-mapper name canonicalization via `/sys/block/<dm-N>/dm/name`.

`canonicalize()` preserves pseudo devices like `none`, `proc`, and `devpts`, falls back to returning the original path on resolution failure, and rewrites private `dm-N` names to `/dev/mapper/<name>` when sysfs exposes the mapper name.
