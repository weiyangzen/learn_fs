# File Research: sources/local-fs/jfsutils/fsck/xfsck.h

Defines common fsck-facing constants, record types, message levels, exit codes, and internal return-code namespaces for `fsck.jfs`.

Key contents:
- Includes `jfs_types.h` and `jfs_dmap.h`, so this header is tied to JFS on-disk integer/extent and block-map definitions.
- Defines non-OS/2 extended attribute list structures `FEA` and `FEALIST`, plus `FEA_NEEDEA` and `ERROR_EA_LIST_INCONSISTENT`.
- Declares `jfs_ValidateFEAList()`.
- Defines message metadata: `fsck_msgid_offset`, `fsck_highest_msgid_defined`, message protocol columns, verbosity levels, message file ids, and fsck log text record types.
- Defines dynamic-storage error object/action ids used by fsck allocation diagnostics.
- Defines `struct fsck_bmap_record`, a large workspace/control record for block-map verification and rebuild, tracking aggregate totals, dmap/control-page buffers, AG free tables, offsets, ordinals, and per-level error flags.
- Defines helper message payload structs `fsck_ino_msg_info` and `fsck_imap_msg_info`.
- Defines `process_extent` operation codes such as `FSCK_RECORD`, `FSCK_RECORD_DUPCHECK`, `FSCK_UNRECORD`, and FSIM variants.
- Defines standard fsck process exit codes: clean, corrected, reboot needed, uncorrected errors, operational error, usage error.
- Defines a large internal status-code space: positive informational codes, negative fatal I/O/metadata codes, and catastrophic `FSCK_INTERNAL_ERROR_*` values.

Interactions:
- Used by fsck modules and by `jfs_fscklog` extraction/display code for return codes, message bounds, and error names.
- `struct fsck_bmap_record` directly references JFS allocation-map structures from `jfs_dmap.h`.

Research notes:
- This is not algorithmic code; it is a central ABI-like constants header for fsck diagnostics and control flow.
- Message-id synchronization is explicitly called out as fragile: `fsck_highest_msgid_defined` must track message tables elsewhere.
