# File Research: sources/local-fs/dosfstools/src/fat.h

Public interface for FAT table operations.

Declared capabilities:
- Load/release FAT state.
- Get/set individual FAT entries.
- Detect bad clusters.
- Traverse chains and map clusters to offsets.
- Set/get cluster ownership.
- Scan for bad clusters.
- Reclaim unowned clusters by freeing or salvaging to files.
- Update FAT32 free-cluster summary.

Role:
- Provides the shared cluster-chain API used by boot/root allocation, directory checking, fsck main flow, and label handling on FAT32.
