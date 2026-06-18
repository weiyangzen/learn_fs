# File Research: sources/local-fs/jfsutils/include/jfs_version.h

Single version-date macro.

Key contents:
- Defines `JFSUTILS_DATE "04-Mar-2011"`.

Interactions:
- `fscklog.c` prints this date alongside package `VERSION`.

Research notes:
- No include guard; intentionally minimal generated/static version metadata.
