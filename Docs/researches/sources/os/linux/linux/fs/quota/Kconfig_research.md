# File Research: sources/os/linux/linux/fs/quota/Kconfig

## Role

Defines kernel quota subsystem configuration.

## Options

- `QUOTA`: core disk quota support; selects `QUOTACTL`.
- `QUOTA_NETLINK_INTERFACE`: netlink quota warning delivery.
- `PRINT_QUOTA_WARNING`: obsolete console quota warnings, gated behind `BROKEN`.
- `QUOTA_DEBUG`: additional quota sanity checks.
- `QUOTA_TREE`: generic tree-structured quota file support.
- `QFMT_V1`: old pre-2.4.22 quota format support.
- `QFMT_V2`: vfsv0/vfsv1 quota format support, selecting `QUOTA_TREE`.
- `QUOTACTL`: hidden bool for quota control syscall support.

## Research Notes

The config distinguishes generic quota infrastructure from on-disk quota formats and notification channels. XFS and GFS2 are noted as using their own quota systems.
