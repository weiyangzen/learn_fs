# File Research: sources/local-fs/exfatprogs/fsck/fsck.c

`fsck.c` is the main implementation for `fsck.exfat`. It validates exFAT boot regions, root metadata, allocation bitmap, upcase table, directory entries, file cluster chains, optional orphan-cluster rescue, and optional recursive MBR state.

The file owns the program globals:
- `struct exfat_fsck exfat_fsck`, holding the mounted exFAT context, directory iterator buffers, repair options, MBR mode, dirty flags, per-directory name hash bitmap, and progress bar.
- `struct exfat_stat exfat_stat`, counting directories, files, errors, and fixes.
- `struct path_resolve_ctx path_resolve_ctx`, used to print path-aware diagnostics.

CLI handling supports `-r/-y/-n/-p/-a`, rescue with `-s`, bad filesystem-name bypass with `-b`, progress with `-P`, verbosity, version/help, and long-only `--put-mbr` / `--clear-mbr`. Write-capable modes are encoded by `FSCK_OPTS_REPAIR_WRITE`; read-only checking defaults to `FSCK_OPTS_REPAIR_NO`. Interactive repair and progress are rejected together.

Boot-region handling is layered:
- `boot_region_checksum()` recomputes the 11-sector boot checksum and compares all words in the checksum sector.
- `read_boot_region()` reads and validates OEM name, checksum, sector size, cluster size, exFAT version, FAT count, volume length, and cluster count.
- `exfat_boot_region_check()` first reads sector size from the main boot sector, optionally allows bad OEM names under `-b`, tries the main region, and can restore from the backup boot region through `restore_boot_region()`.
- `exfat_mark_volume_dirty()` sets or clears the VolumeDirty flag in the boot sector and fsyncs after write.

Cluster-chain checking is central to consistency:
- `check_clus_chain()` validates a file or vendor-allocation dentry stream against file size, first cluster, FAT chain, heap bounds, duplicate cluster usage, BAD clusters, free-on-disk clusters, and too-short/too-long chains. Repair truncates the stream, updates stream dentries, and may terminate FAT at the last valid cluster.
- `root_check_clus_chain()` performs similar traversal for the root directory and guards against cyclic or broken root chains.
- The in-memory `alloc_bitmap` is populated as reachable clusters are discovered, then later compared/written against the on-disk allocation bitmap.

Directory-entry validation flows through:
- `file_calc_checksum()` recomputes a file dentry set checksum.
- `read_file_dentry_set()` validates the primary file dentry, stream dentry, name dentries, secondary counts, vendor extension/allocation entries, stream valid size, unknown dentries, and deletion/skip behavior for unrecoverable dentry sets.
- `check_name_dentry_set()` validates UTF-16 name length, invalid characters, name hash, and per-directory duplicate-name hashes. Duplicate or invalid names can route to `exfat_repair_rename_ask()`.
- `handle_dot_dotdot_filename()` rejects all-dot names that are not allowed on exFAT.
- `check_inode()` validates cluster chain, file size against cluster heap, empty contiguous streams, directory size alignment, and dentry-set checksum repair.

Root metadata checks are in `exfat_root_dir_check()`: it initializes root cluster/size, reads the volume label, reads the allocation bitmap, reads or repairs the upcase table, and builds an in-memory root dentry set. `read_bitmap()` validates bitmap dentry size and start cluster, stores bitmap cluster/size in `struct exfat`, marks bitmap clusters allocated, and loads the disk bitmap.

Upcase handling includes:
- `decompress_upcase_table()`, which expands compressed 0xFFFF skip-runs into a full uppercase mapping.
- `read_upcase_table()`, which locates the root upcase dentry, validates cluster, size, contents, and checksum, marks its clusters allocated, and falls back to the built-in default table when invalid.
- `exfat_repair_upcase_table()`, which writes the default upcase table and root dentry if the table entry or data is missing/corrupt.

Filesystem traversal is breadth/list based:
- `read_children()` iterates dentries in a directory, processes file dentry sets, handles `EXFAT_LAST` with `check_unused_dentry()`, tolerates root-only metadata entries, and repairs unknown live dentries by deleting them when permitted.
- `exfat_filesystem_check()` seeds `exfat->dir_list` with root, walks queued subdirectories, frees file children and ancestors as traversal advances, and cleans up the directory list.

Allocation reconciliation:
- `write_bitmap()` writes only changed 512-byte-aligned bitmap segments, using `alloc_bitmap | disk_bitmap`; this preserves already-marked allocated clusters unless rescue or other repair changes state.
- `rescue_orphan_clusters()` computes clusters marked allocated on disk but not referenced by scanned files, creates `LOST+FOUND`, and creates contiguous `FILE%07d.CHK` entries for orphan ranges.

MBR-related code:
- `do_recursive_mbr()` checks for copy-protected MBR markers, recognizes already-recursive MBR partition state, selects whether a partition table is suitable for Windows, and asks to write a recursive MBR when needed.
- `do_put_mbr()` rewrites bootstrap/partition entries in both main and backup boot regions, recalculates boot checksums, and can either place a recursive partition entry or clear partition entries.

`main()` wires the complete workflow: parse options, open block device, validate/repair boot region, handle MBR mode, allocate root/exFAT/buffers, mark volume dirty for write repairs, check root, optionally initialize progress by used cluster count, traverse filesystem, optionally rescue orphan clusters, write bitmap, fsync, clear VolumeDirty, print summary, free resources, and return fsck-style exit bits.

Notable dependencies are `libexfat` for device I/O, FAT/bitmap operations, dentry iterators, name encoding/hash/checks, path resolution, progress bar, and boot checksum helpers; `repair.c` supplies all user/auto repair decisions.
