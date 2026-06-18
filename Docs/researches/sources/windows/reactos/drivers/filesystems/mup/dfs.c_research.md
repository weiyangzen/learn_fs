# File Research: sources/windows/reactos/drivers/filesystems/mup/dfs.c

This file contains DFS entry points used by MUP when DFS support is enabled, but all functionality is currently stubbed.

`DfsVolumePassThrough`, `DfsFsdFileSystemControl`, `DfsFsdCreate`, `DfsFsdCleanup`, and `DfsFsdClose` return `STATUS_NOT_IMPLEMENTED`. `DfsUnload` is also unimplemented. `DfsDriverEntry` logs that DFS is not implemented and returns `STATUS_NOT_IMPLEMENTED`.

Research notes:
- `mup.c` attempts DFS initialization if registry policy allows it, but disables DFS if `DfsDriverEntry` fails.
- These stubs keep DFS dispatch boundaries visible without enabling DFS behavior.
