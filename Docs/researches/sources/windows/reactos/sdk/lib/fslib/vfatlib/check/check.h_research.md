# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/check.h

This header declares the FAT directory checker interface.

Core contents:
- `alloc_rootdir_entry` allocates or creates a root directory slot, optionally generating a unique name from a printf-style pattern.
- `scan_root` scans root and subdirectories, returning nonzero when another check pass is needed.

Risk points:
- The API depends on global checker state such as `n_files`, `interactive`, `rw`, LFN state, and file selection state.
- `alloc_rootdir_entry` can extend FAT32 root directory chains and write to disk.
