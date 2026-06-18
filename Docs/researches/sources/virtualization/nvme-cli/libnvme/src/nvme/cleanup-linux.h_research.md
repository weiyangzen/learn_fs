# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/cleanup-linux.h

Linux-specific cleanup helpers built on GCC/Clang `__attribute__((cleanup))`.

Exports/macros:
- `__cleanup_file`: closes `FILE *` with `fclose`.
- `__cleanup_dir`: closes `DIR *` with `closedir`.
- `__cleanup_fd`: closes an `int` file descriptor when it is `>= 0`.

Dependencies:
- Includes `<dirent.h>`, `<stdio.h>`, `<unistd.h>`, and `cleanup.h`.

Integration:
- Used in `crypto.c` and `fabrics.c` to make early returns close files/directories/fds.
- Complements generic pointer cleanup in `cleanup.h`.

Risks:
- Assumes GCC-compatible cleanup attributes.
- `cleanup_fd` requires variables to be initialized to `-1` before use.
- Cleanup functions ignore close errors, which is acceptable for most read/scan paths but not for durability-sensitive write paths.
