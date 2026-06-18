# File Research: sources/os/linux/linux-stable/fs/ntfs/volume.h

This header defines the legacy NTFS in-memory volume structure and related volume-flag and accounting helpers.

Main responsibilities:
- Declares `struct ntfs_volume`, the central superblock-private state used by `fs/ntfs`.
- Defines bit positions for mount/volume behavior flags and emits inline `NVol*`, `NVolSet*`, and `NVolClear*` helpers.
- Provides inline helpers for free cluster, free MFT record, LCN bitmap, and dirty-cluster reservation accounting.
- Declares `ntfs_available_clusters_count()` and `get_nr_free_clusters()` implemented in `super.c`.

Important fields in `struct ntfs_volume`:
- VFS/mount state: `sb`, `flags`, `uid`, `gid`, permission masks, `on_errors`, `wb_err`, `nls_map`, and `nls_utf8`.
- Geometry: sector, cluster, MFT record, and index record sizes plus masks and shifts.
- Volume layout: cluster count, `$MFT` and `$MFTMirr` LCNs, mirror size, serial number, MFT/data allocation zone positions.
- Metadata inodes: `$MFT`, `$MFT/$BITMAP`, `$MFTMirr`, `$LogFile`, `$Bitmap`, `$Volume`, root, `$Secure`, `$Extend`, `$Quota`, and `$Quota/$Q`.
- Metadata tables: `$UpCase`, `$AttrDef`, volume flags/version, and volume label.
- Allocation accounting: `free_waitq`, `free_clusters`, `free_mft_records`, `dirty_clusters`, sparse compression unit, `lcn_empty_bits_per_page`, and background `precalc_work`.

Volume flags:
- Include errors, system-file visibility, case sensitivity, logfile empty, quota state, USN journal state, read-only, compression, known free-cluster count, shutdown, system-file immutability, hidden/dot-file policies, Windows-name checking, discard, and sparse disabling.

Research notes:
- The inline free-cluster helpers wait until `NVolFreeClusterKnown()` is set; this couples allocation accounting to the background scan started by `super.c`.
- `dirty_clusters` tracks reserved or delayed allocation pressure separately from committed free-cluster counts.
