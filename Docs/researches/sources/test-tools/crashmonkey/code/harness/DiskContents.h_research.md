# sources/test-tools/crashmonkey/code/harness/DiskContents.h

Purpose: declares the `fileAttributes` and `DiskContents` helpers for comparing mounted file-system contents and validating crash-state images.

Important APIs/types: `fileAttributes` exposes captured `dirent`, `stat`, and md5 data plus setters/comparators. `DiskContents` exposes mount/unmount, mount-point setters, full-disk comparison, path comparison, range comparison, recursive deletion/creation helpers, and `sanity_checks()`.

Control flow and integration: `Tester` constructs these objects during automated check mode. The private `get_contents()` recursively builds the content map, while public comparison functions orchestrate mounting and reporting.

State: private fields track whether a disk was mounted, the source device path, mount point, fs type, and a map from relative path to attributes. The header implies objects are stateful and not reusable safely without clearing `contents`.

Dependencies: includes Linux/POSIX filesystem headers and C++ streams/maps. The interface is tied to Unix path strings and block-device mount semantics.

Risks and test signals: the private declaration `compare_contents()` is not implemented in the read file set, suggesting stale design. Tests should validate that repeated calls do not retain stale map entries, that mount-point lifecycle is correct, and that special files/symlinks are handled intentionally.
