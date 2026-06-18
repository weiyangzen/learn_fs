# File Research: sources/os/bsd/openbsd-src/sys/sys/disk.h

This header defines kernel disk objects, disk statistics, and disk-list interfaces.

Key definitions:
- `DS_DISKNAMELEN`
- `struct diskstats`
- `struct disk` with global-list linkage, locks, device identity, flags, statistics, open masks, label state, block/byte shifts, and dynamically allocated `disklabel`.
- Disk flags: `DKF_CONSTRUCTED`, `DKF_OPENED`, `DKF_NOLABELREAD`.
- Disk label states: `DK_CLOSED`, `DK_WANTOPEN`, `DK_WANTOPENRAW`, `DK_RDLABEL`, `DK_OPEN`, `DK_OPENRAW`.
- Disk map flags: `DM_OPENPART`, `DM_OPENBLCK`.
- Public `TAILQ_HEAD(disklist_head, disk)`.

Kernel APIs:
- Lifecycle/statistics: `disk_init`, `disk_construct`, `disk_attach`, `disk_detach`, `disk_busy`, `disk_unbusy`, `disk_gone`.
- Partition/open handling: `disk_openpart`, `disk_closepart`.
- Lock/lookup: `disk_lock`, `disk_lock_nointr`, `disk_unlock`, `disk_lookup`.
- Labels/map/DUID: `disk_readlabel`, `disk_map`, `duid_iszero`, `duid_format`.

Risk notes:
- Open masks are 64-bit to match `MAXPARTITIONSUNIT`.
- `dk_label` is dynamically allocated to avoid machine-dependent `struct disk` sizing.
