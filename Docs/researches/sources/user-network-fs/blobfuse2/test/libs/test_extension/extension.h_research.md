<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension/extension.h -->
# sources/user-network-fs/blobfuse2/test/libs/test_extension/extension.h

Source path: `sources/user-network-fs/blobfuse2/test/libs/test_extension/extension.h`

## Purpose
Defines the public extension contract for blobfuse/blobfuse2 extension modules using FUSE2 `FUSE_USE_VERSION 29`.

## Important APIs, Types, And Functions
Functions/prototypes: none declared. Includes: `stddef.h`, `stdio.h`, `fuse.h`. Defines: `__EXTENSION_H__`, `FUSE_USE_VERSION`.

## Control Flow
The header exposes the handshake, initialization, FUSE callback registration, and backend storage callback registration functions. It also declares a global `struct fuse_operations storage_callbacks` that extension handlers use to call back into the storage implementation.

## State And Persistence
State is process-local C state plus filesystem effects through FUSE/POSIX operations. Extension files rely on the global `storage_callbacks` table and, for FUSE3 registration, `signature_verified`; utility programs persist only the files or directory entries they create through the mounted filesystem.

## Dependencies And Integration Points
Depends on `stddef.h`, `stdio.h`, `fuse.h` and integrates with blobfuse2's extension loader, libfuse callback dispatch, or shell-driven test harnesses under `test/scripts`.

## Risks
The global callback declaration in a header can create multiple definitions if included in more than one compilation unit without external linkage controls. ABI compatibility depends on matching the exact libfuse version and `struct fuse_operations` layout expected by the loader.

## Test Signals
Useful signals are successful compilation against the target FUSE headers, expected exit status from helper programs, syslog/debug output for extension callbacks, and observable mount-side behavior such as hidden paths, flushed writes, or directory offset handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension/extension.h -->
