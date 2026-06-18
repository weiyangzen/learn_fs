# sources/sync-backup/git-lfs/tools/util_windows.go

Purpose: Windows block cloning support using `FSCTL_DUPLICATE_EXTENTS_TO_FILE`.

Important APIs/types/functions: `availableClusterSize`, `GiB`, `fsctlDuplicateExtentsToFile`, `duplicateExtentsData`, `CheckCloneFileSupported`, `CloneFileByPath`, `CloneFile`, `callDuplicateExtentsToFile`, and `roundUp`.

Control flow: probe writes non-empty temp source and clones to temp destination. `CloneFile` requires `*os.File`, truncates destination to source size, clones full GiB chunks, then clones the tail rounded to 64 KiB or 4 KiB cluster sizes.

State and persistence: mutates destination size and extents; creates/removes temp probe files.

Dependencies and integration points: called by `CopyWithCallback` on Windows for ReFS block clone support. Depends on `x/sys/windows` and unsafe IOCTL calls.

Risks: destination is not opened with truncation in `CloneFileByPath` but `CloneFile` truncates to source size. Filesystem cluster requirements are handled by retrying two sizes, but unsupported filesystems return errors. Large-file loop and rounding must avoid overflow.

Test signals: Windows tests cover clone correctness over many sizes when `REFS_TEST_DIR` or current directory supports cloning.
