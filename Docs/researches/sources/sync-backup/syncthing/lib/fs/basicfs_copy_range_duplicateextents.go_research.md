## sources/sync-backup/syncthing/lib/fs/basicfs_copy_range_duplicateextents.go

Purpose: Windows copy-range backend using `FSCTL_DUPLICATE_EXTENTS_TO_FILE` block cloning.

Important APIs/types/functions: Registers `CopyRangeMethodDuplicateExtents`; constants/vars `availableClusterSize`, `GiB`, `fsctlDuplicateExtentsToFile`; struct `duplicateExtentsData`; functions `copyRangeDuplicateExtents`, `wrapError`, `callDuplicateExtentsToFile`, and `roundUp`.

Control flow: Ensures destination is large enough, verifies source length, validates 4 KiB boundary requirements, clones whole GiB chunks, then tries tail clone rounded to 64 KiB and falls back to 4 KiB. DeviceIoControl performs the actual clone.

State and persistence: May truncate destination to fit target range and clone filesystem extents. No other persistence.

Dependencies and integration points: Windows build tag; uses Windows syscalls and copy-range registry.

Risks: Filesystem constraints are strict; nonaligned offsets and unsupported filesystems return errors/fallback. `wrapError` maps a Windows severity error to `ENOTSUP`; other platform errors pass through.

Test signals: No direct tests in this subset; requires Windows/filesystem-specific integration coverage.
