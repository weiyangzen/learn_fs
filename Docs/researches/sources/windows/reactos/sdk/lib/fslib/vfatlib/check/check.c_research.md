# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/check.c

This file is the core FAT directory tree checker and repair engine.

Core responsibilities:
- Allocates root directory entries for recovered files.
- Builds printable paths and file metadata summaries.
- Validates 8.3 names, `.`/`..` entries, duplicate directory entries, directory sizes, start clusters, cluster chains, shared clusters, bad/free clusters in chains, and file size versus chain length.
- Tracks long filename slots through the LFN helpers.
- Builds an in-memory `DOS_FILE` tree while scanning root and subdirectories.
- Handles configured drop/undelete requests through `file.c`.
- Performs read-test bad cluster checks and circular-chain truncation.
- Recursively scans all subdirectories via `scan_root`.

Important behavior:
- `FSTART` combines low/high start cluster fields for FAT32.
- `MODIFY` and `MODIFY_START` update directory entries or FAT32 root cluster metadata in place.
- Cluster ownership is first used during read-test loop detection, then reset, and later used for final cross-link detection.
- Orphaned LFN slots are checked when free or non-LFN entries interrupt a sequence.
- Root directory is special: FAT32 root has a synthetic entry with offset zero.

ReactOS-specific behavior:
- Several repair actions are gated by `rw`; in read-only mode the checker reports but avoids writes.
- Manual rename returns immediately under ReactOS.
- File-stat formatting uses ReactOS time conversion APIs.
- Some old behavior remains under `__REACTOS__`, including suspicious-name handling and output differences.

Risk points:
- Many fatal cases call `die`, which terminates the hosting process.
- Several “can’t fix this yet” cases remain for missing `.` or `..`.
- In read-only mode, some paths still compute as if repairs occurred but skip writes.
- Directory buffer and tree nodes are managed through qalloc/free queues outside this file, so lifecycle depends on surrounding checker code.
