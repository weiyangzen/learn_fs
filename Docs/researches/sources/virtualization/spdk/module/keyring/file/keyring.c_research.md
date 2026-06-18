# File Research: sources/virtualization/spdk/module/keyring/file/keyring.c

Implements a keyring backend that reads key material from local files.

Key elements:
- Validates paths as absolute.
- Requires key files to have no group/other permission bits.
- Requires key files to be owned by the current user.
- Stores key context as the configured file path.
- Reads key material with `fopen()`/`fread()` after rechecking path metadata.
- Emits config JSON as `keyring_file_add_key` with name and path.
- Exposes `spdk_keyring_file_add_key()` and `spdk_keyring_file_remove_key()`.
- Registers keyring module `keyring_file`.

Dependencies:
- SPDK keyring module API, file key module header, logging, string, and util APIs.

Research notes:
- Key material is not cached by this backend; it is loaded from the file when requested.
