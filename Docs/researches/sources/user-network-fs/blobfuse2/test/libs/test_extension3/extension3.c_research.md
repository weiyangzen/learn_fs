<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension3/extension3.c -->
# sources/user-network-fs/blobfuse2/test/libs/test_extension3/extension3.c

Source path: `sources/user-network-fs/blobfuse2/test/libs/test_extension3/extension3.c`

## Purpose
Provides the FUSE3 sample extension entrypoints that blobfuse2 loads from a shared object or static library.

## Important APIs, Types, And Functions
Functions/prototypes: `validate_signature`, `init_extension`, `register_fuse_callbacks`, `register_storage_callbacks`. Includes: `stdio.h`, `stdlib.h`, `syslog.h`, `string.h`, `extension3.h`, `callback_handler.h`. Defines: none declared.

## Control Flow
`validate_signature` compares the launcher token with `ola-amigo-3!!`, sets global `signature_verified`, and returns the extension token. `register_fuse_callbacks` refuses registration until the handshake passes, then fills a FUSE operation table with `ext_*` handlers. `register_storage_callbacks` stores blobfuse's callback table in the global `storage_callbacks` value.

## State And Persistence
State is process-local C state plus filesystem effects through FUSE/POSIX operations. Extension files rely on the global `storage_callbacks` table and, for FUSE3 registration, `signature_verified`; utility programs persist only the files or directory entries they create through the mounted filesystem.

## Dependencies And Integration Points
Depends on `stdio.h`, `stdlib.h`, `syslog.h`, `string.h`, `extension3.h`, `callback_handler.h` and integrates with blobfuse2's extension loader, libfuse callback dispatch, or shell-driven test harnesses under `test/scripts`.

## Risks
The handshake is a fixed string check, not cryptographic authentication. `signature_verified` and `storage_callbacks` are process globals, so reloads or multiple consumers can overwrite shared state. `init_extension` only logs the config path and does not validate or persist configuration.

## Test Signals
Useful signals are successful compilation against the target FUSE headers, expected exit status from helper programs, syslog/debug output for extension callbacks, and observable mount-side behavior such as hidden paths, flushed writes, or directory offset handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension3/extension3.c -->
