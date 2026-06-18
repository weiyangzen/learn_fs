<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension/extension.c -->
# sources/user-network-fs/blobfuse2/test/libs/test_extension/extension.c

## Purpose
Sample extension entrypoints used by Blobfuse2 to validate an extension signature and exchange FUSE callback tables.

## Important APIs, Types, and Functions
Globals `signature_verified`, `launcher_call_sign`, and `my_call_sign` implement a handshake. `validate_signature` checks the launcher's string and returns the extension response string. `init_extension` logs the received config file. `register_fuse_callbacks` populates a provided `fuse_operations` table with local `ext_*` wrappers after signature verification. `register_storage_callbacks` copies Blobfuse2 storage callbacks into global `storage_callbacks`.

## Control Flow and State
Blobfuse2 is expected to call `validate_signature`, then `init_extension`, then registration functions. Until signature verification succeeds, registration returns `-1`. After storage callbacks are registered, wrapper functions in `callback_handler.c` can forward FUSE operations.

## Dependencies and Integration Points
Includes `extension.h` and `callback_handler.h`; depends on FUSE and syslog. This file is the dynamic-library boundary used by Blobfuse2 extension support.

## Risks and Edge Cases
The signature handshake is a simple string comparison and not security-sensitive authentication. `signature_verified` is global and not thread-safe, though registration is likely single-threaded. Callback table assignment assumes ABI compatibility with the FUSE version.

## Test Signals
Syslog entries and successful return from callback registration indicate extension loading. Negative testing can call registration before signature verification and expect failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension/extension.c -->
