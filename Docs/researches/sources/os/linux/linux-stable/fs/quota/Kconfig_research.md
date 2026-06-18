# File Research: sources/os/linux/linux-stable/fs/quota/Kconfig

## Summary
Defines Kconfig options for Linux VFS quota support and quota file formats.

## Main Responsibilities
- Define core `QUOTA` support and select `QUOTACTL`.
- Configure optional netlink quota warning reporting.
- Retain obsolete console quota warning option behind `BROKEN`.
- Enable quota sanity checking with `QUOTA_DEBUG`.
- Define generic tree-structured quota file support as `QUOTA_TREE`.
- Enable old V1 quota format support with `QFMT_V1`.
- Enable VFS V0/V1 quota format support with `QFMT_V2`, selecting `QUOTA_TREE`.
- Define internal `QUOTACTL`.

## Cross-File Interactions
Controls the quota objects built by `fs/quota/Makefile` and the availability of VFS quota syscalls, warning paths, and on-disk quota format parsers.
