# sources/test-tools/stress-ng/stress-rofs.c

Purpose: implements `rofs`, a read-only filesystem stressor that discovers or accepts read-only mount points, recursively scans them, and exercises metadata/read-only operations while checking that paths are not writable.

Important APIs/types/functions: `stress_rofs_info_t` stores directory entry metadata, lstat result, and writable flag. `stress_rofs_method_t` maps method names to per-file functions. Methods include lstat, statx, access, mmap read, random read, lseek including `SEEK_HOLE`/`SEEK_DATA`, xattr listing, flock, valid and invalid open/close, fsync, and filesystem ioctls. `stress_rofs_scandir()` drives recursion and metrics. `stress_rofs_info` exposes `rofs-dir`.

Control flow: `stress_rofs()` initializes metrics, validates an explicit `rofs-dir` if supplied, or scans mounts with `stress_mount_get()` and `statfs()` for `ST_RDONLY`, skipping `/sys`, configfs, and cgroup mounts. It logs selected paths, synchronizes, then rotates instances across paths. `stress_rofs_scandir()` opens a directory, rejects writable directories, snapshots entries into a linked list, runs every method over every entry, increments bogo once per directory scan, recurses into subdirectories, and fails if any entry was writable.

State and persistence: only in-memory linked lists, stat buffers, metric counters, and mount path arrays persist during execution. File descriptors and mappings are short-lived. No files are created; invalid write attempts must fail on the target filesystem.

Dependencies and integration points: integrates with Linux mount helpers, optional xattr headers, optional `statx`, `flock`, `statvfs/statfs`, ioctl definitions from `linux/fs.h`, stress-ng mmap helpers, metrics, settings, and path helpers.

Risks and test signals: read-only detection can race with remounts or permission changes, and access checks have TOCTOU exposure acknowledged in code. Device pseudo-files may reject operations differently. Metrics report per-method operation rates; failure signals include unexpected writability, unexpected writable mmap/open, or unexpected metadata/read errors not whitelisted.
