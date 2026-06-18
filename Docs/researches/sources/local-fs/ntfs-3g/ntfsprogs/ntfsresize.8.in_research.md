# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsresize.8.in

This file is the roff manual page template for `ntfsresize`, the NTFS-3G utility for resizing NTFS filesystems. It documents syntax, safety model, shrinking/enlarging workflows, partition-table responsibilities, options, exit status, known issues, authorship, availability, and related tools. The `@VERSION@` token is substituted by the build system.

The manual emphasizes that `ntfsresize` resizes the filesystem, not the containing partition. For shrinkage, users should shrink the NTFS filesystem first and then shrink the partition without making it smaller than the filesystem. For enlargement, users should enlarge the partition first and then grow the filesystem. It warns that partition recreation must preserve the same starting sector and partition type, and the bootable flag when applicable.

Documented operating modes include `--check`, `--info`, `--info-mb-only`, `--size`, `--expand`, `--force`, `--no-action`, `--bad-sectors`, `--no-progress-bar`, `--verbose`, `--version`, and `--help`. Size suffixes use SI decimal units for `k`, `M`, and `G`, while binary `ki`, `Mi`, and `Gi` are also accepted. `--no-action` is recommended before real resizing.

The `--expand` section describes downward expansion that keeps the filesystem end fixed and shifts the beginning, recreating metadata in the expanded space without relocating user data. It highlights compatibility constraints: exact cluster-size multiple, enough space for new metadata, incompatibility with `--size`, and possible boot issues for Windows system partitions.

Safety notes are prominent. The page recommends regular backups, suggests `ntfsclone`, explains that real resizing marks NTFS for Windows `chkdsk`, and describes when `--force` is appropriate. `--bad-sectors` is framed as a workaround for hardware defects, with strong advice to back up and run Windows `chkdsk /f /r`.

Known limitations include unknown bad sectors, relocation of the first MFT extent, and resizing into the middle of an `$MFTMirr` extent. The page also documents historical Linux disk-geometry/partition-table issues involving partitioning tools, clarifying that `ntfsresize` itself does not alter partition tables.

Risks and invariants: this is documentation rather than executable code, but it is user-facing safety documentation for a destructive-capable filesystem tool. Accuracy matters because the manual tells users the required ordering between filesystem and partition resizing, when read-only info modes are used, and when Windows consistency checks are expected.
