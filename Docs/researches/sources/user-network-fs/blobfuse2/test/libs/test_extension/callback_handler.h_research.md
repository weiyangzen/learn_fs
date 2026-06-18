<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension/callback_handler.h -->
# sources/user-network-fs/blobfuse2/test/libs/test_extension/callback_handler.h

## Purpose
Header declaring the sample extension callback functions implemented in `callback_handler.c`.

## Important APIs, Types, and Functions
Defines include guard `__CALLBACK_HANDLERS_H__`, sets `FUSE_USE_VERSION 29`, includes `<fuse.h>`, and declares `ext_*` functions for init/destroy, stat/getattr, directory operations, file operations, symlink/readlink, fsync/fsyncdir, and chmod.

## Control Flow and State
No runtime flow or state. It provides the compile-time contract between `extension.c` and `callback_handler.c`.

## Dependencies and Integration Points
Depends on libfuse headers. Comments document commands to build a shared or static extension library.

## Risks and Edge Cases
FUSE 2.9 is hard-coded; building against FUSE 3 without compatibility may fail. The include guard name differs from the filename singular/plural pattern, but remains functional.

## Test Signals
Successful compilation of the extension is the main validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension/callback_handler.h -->
