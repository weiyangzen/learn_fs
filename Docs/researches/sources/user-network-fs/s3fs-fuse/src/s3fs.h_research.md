# sources/user-network-fs/s3fs-fuse/src/s3fs.h

## Purpose

This header provides the small FUSE-facing compatibility layer used by the s3fs main implementation. It selects the libfuse API version, disables FUSE-T's Darwin-specific operation overloading on macOS, includes `fuse.h`, defines a fallback fill-dir flag constant for older FUSE versions, and defines a convenience macro for exiting the active FUSE loop.

## Important APIs, Types, and Functions

- `FUSE_USE_VERSION 30`: requests the libfuse 3 API surface before including `fuse.h`.
- `FUSE_DARWIN_ENABLE_EXTENSIONS 0` and `FUSE_DARWIN_OVERLOAD_OPERATIONS 0`: on Apple platforms, opt out of FUSE-T overloads so callback signatures continue to match upstream libfuse3 signatures used in `s3fs.cpp`.
- `S3FS_FUSE_FILL_DIR_DEFAULTS`: a `constexpr fuse_fill_dir_flags` value set to zero. The comment notes that `FUSE_FILL_DIR_DEFAULTS` requires FUSE 3.17, so this constant preserves compatibility with older libfuse3 headers.
- `S3FS_FUSE_EXIT()`: macro that obtains `fuse_get_context()`, checks it, and calls `fuse_exit(pcxt->fuse)`.

## Control Flow

There is no runtime control flow besides the macro expansion. Consumers include this header before declaring or assigning FUSE callbacks. Directory-reading code passes `S3FS_FUSE_FILL_DIR_DEFAULTS` to the FUSE filler callback when inserting `.` and `..`. Error paths that want to terminate the FUSE loop can use `S3FS_FUSE_EXIT()`, although `s3fs.cpp` currently has a local `s3fs_exit_fuseloop()` helper for startup failures.

## State and Persistence Behavior

This header owns no persistent state and no process state beyond compile-time preprocessor configuration. Its choices affect ABI compatibility with libfuse and platform-specific callback signatures, not filesystem metadata or S3 persistence.

## Dependencies and Integration Points

The direct dependency is `<fuse.h>`. The header must be included in translation units that need libfuse declarations after `FUSE_USE_VERSION` is set. It is included by `s3fs.cpp`, where the `fuse_operations` table is populated and where `S3FS_FUSE_FILL_DIR_DEFAULTS` is used in `s3fs_readdir()`.

The Apple-specific defines are an integration point with FUSE-T's libfuse3 fork. They reduce platform divergence by forcing standard libfuse3 signatures instead of Darwin-specific overloaded types such as `fuse_darwin_attr`.

## Risks and Edge Cases

Because `FUSE_USE_VERSION` must be defined before `fuse.h`, include order matters. A translation unit that includes `fuse.h` first with a different version could see incompatible declarations. The zero-valued fill-dir constant is intentionally compatible with older FUSE headers, but it also means newer named defaults are not used directly. The exit macro is safe against a null FUSE context, but it silently does nothing when called outside a FUSE callback context.

## Test Signals

Build tests should cover Linux, macOS/FUSE-T, and any WinFsp/MSYS build variants that include this header. Compile checks should verify that all callback signatures in `s3fs.cpp` match the selected libfuse headers. Runtime smoke tests for `readdir` should verify that `.` and `..` are filled correctly with the zero fill-dir flags on older and newer FUSE 3 versions.
