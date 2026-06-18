<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension/callback_handler.c -->
# sources/user-network-fs/blobfuse2/test/libs/test_extension/callback_handler.c

## Purpose
Sample Blobfuse2 FUSE extension callback implementation that wraps storage callbacks, logs calls, and demonstrates filtering one path.

## Important APIs, Types, and Functions
Implements `ext_init`, `ext_destroy`, and wrappers for `statfs`, `getattr`, directory operations, file operations, symlink/readlink, fsync/fsyncdir, and chmod. Most functions log to syslog and forward to the corresponding function in external `storage_callbacks`. `ext_getattr` returns `-ENOENT` for `/subtree.sh`.

## Control Flow and State
The file does not own persistent state. It relies on the global `storage_callbacks` populated by `extension.c`. Init/destroy call through if present; most other methods assume callbacks are populated and call directly.

## Dependencies and Integration Points
Includes `extension.h`; depends on FUSE 2.9 types and syslog. Compiled into `libextension.so` with `extension.c`. Integrates with Blobfuse2 extension loading.

## Risks and Edge Cases
Most wrappers do not check for null function pointers, so incomplete callback registration can crash. The hard-coded `/subtree.sh` filter changes filesystem semantics and is suitable only as sample/test behavior. Signature differences must match the FUSE version expected by Blobfuse2.

## Test Signals
Syslog messages confirm callback routing. Filtering `/subtree.sh` can be used to verify extension interception.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension/callback_handler.c -->
