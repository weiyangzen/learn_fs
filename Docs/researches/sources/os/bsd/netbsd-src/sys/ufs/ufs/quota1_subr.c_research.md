# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota1_subr.c

This file converts between legacy quota1 records and generic quota values.

Key behavior:
- Treats quota1 limit value `0` as unlimited and otherwise stores `limit + 1` style values.
- `dqblk_to_quotavals` converts block and file quotas from `struct dqblk` into `struct quotaval`.
- `quotavals_to_dqblk` converts generic block/file quota values back to quota1 records.
- Notes unresolved handling of `qv_grace`.

Role:
- Thin compatibility adapter for old quota format consumers.
