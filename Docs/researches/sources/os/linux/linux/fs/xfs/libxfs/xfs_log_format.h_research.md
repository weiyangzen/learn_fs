# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_log_format.h

This header defines the on-disk journal/log ABI for XFS, including physical log records, transaction headers, inode/buffer log items, deferred intent formats, quota log items, inode creation records, and attr operation records.

Major contents:
- Physical log constants: iclog counts, record sizes, header size, log versions, LSN helpers, and format tags.
- Log operation header and transaction header definitions.
- Log item type constants for inode, buffer, quota, inode-create, bmap intent/done, rmap intent/done, refcount intent/done, attr intent/done, mapping exchange intent/done, and realtime variants.
- Inode log format structures, including old 32-bit packed format.
- Inode log field flags such as `XFS_ILOG_CORE`, fork data/extent/root flags, owner-rewrite flags, and in-memory-only timestamp/iversion flags.
- `struct xfs_log_dinode`, the host-order logged mirror of `struct xfs_dinode`.
- Buffer log format, dirty bitmap definitions, buffer type encoding in `blf_flags`.
- EFI/EFD extent free intent/done formats with 32-bit and 64-bit compatibility extent layouts.
- RUI/RUD, CUI/CUD, BUI/BUD deferred intent/done formats.
- XMI/XMD mapping exchange formats and logged exchange flags.
- Quota log formats and quota mount/accounting/enforcement flags.
- Inode-create log record.
- Attr intent/done formats, including parent pointer operation opcodes.

Important ABI considerations:
- Many structures have fixed layout assumptions consumed by recovery and checked in `xfs_ondisk.h`.
- Some fields are host order by historical design, not pure disk endian format.
- Compatibility layouts exist for old 32-bit/i386 alignment differences.
- Variable-length intent structures use flexible arrays and helper `sizeof` functions.

Risk notes:
- This is recovery-visible persistent format; changes require extreme compatibility care.
- In-memory-only flags must never be written into recovered on-disk log item fields.
- Log item type values and struct layouts are effectively ABI.
