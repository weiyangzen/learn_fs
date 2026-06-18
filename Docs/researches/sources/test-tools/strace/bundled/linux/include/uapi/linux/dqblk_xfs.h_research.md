# sources/test-tools/strace/bundled/linux/include/uapi/linux/dqblk_xfs.h

Purpose: defines XFS-specific quota `quotactl(2)` command values, quota record layouts, field masks, and quota subsystem status structures.

Important APIs/types/functions: command macros include `XQM_CMD`, `XQM_COMMAND`, quota type IDs, and `Q_XQUOTAON`, `Q_XQUOTAOFF`, `Q_XGETQUOTA`, `Q_XSETQLIM`, `Q_XGETQSTAT`, `Q_XQUOTARM`, `Q_XQUOTASYNC`, `Q_XGETQSTATV`, and `Q_XGETNEXTQUOTA`. Main types are `fs_disk_quota_t`, `fs_qfilestat_t`, `fs_quota_stat_t`, `struct fs_qfilestatv`, and `struct fs_quota_statv`. Field masks cover limits, timers, warning counts, accounting values, and `FS_DQ_BIGTIME`. Flags distinguish user/group/project quota accounting and enforcement.

Control flow: no implementation exists. The ABI flow is callers issuing XFS quota commands through `quotactl`, passing or receiving the relevant struct; `Q_XSETQLIM` uses `d_fieldmask` to select which fields mutate.

State and persistence behavior: quota limits, counters, grace timers, warning counters, and accounting/enforcement flags are persistent filesystem quota state. Status structs are snapshots of quota files and incore dquot counts. Bigtime timer support stores 40-bit signed expiration timestamps split between base timer and high-byte fields.

Dependencies: includes `<linux/types.h>`.

Integration points: strace decodes XFS quota commands, quota types, field masks, and payload structures. XFS quota tools depend on command encodings forming the first `QCMD` argument.

Risks: units are 512-byte basic blocks, not filesystem blocks. Timer semantics differ for superuser dquots versus ordinary dquots. Versioned `fs_quota_statv` requires retrying lower versions on `EINVAL`; decoders should show requested and returned versions clearly.

Test signals: quotactl decode tests should cover `Q_XGETQUOTA`, `Q_XSETQLIM` with mixed field masks, `Q_XGETQSTATV` including project quota fields, bigtime flags, and user/group/project quota type flags.
