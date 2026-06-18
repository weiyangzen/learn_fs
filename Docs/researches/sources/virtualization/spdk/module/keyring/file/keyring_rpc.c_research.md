# File Research: sources/virtualization/spdk/module/keyring/file/keyring_rpc.c

Adds runtime JSON-RPC control for file-backed keyring keys.

Key elements:
- Registers `keyring_file_add_key`.
- Decodes `name` and `path`, calls `spdk_keyring_file_add_key()`, returns boolean success.
- Registers `keyring_file_remove_key`.
- Decodes `name`, calls `spdk_keyring_file_remove_key()`, returns boolean success.

Dependencies:
- SPDK JSON-RPC, string/util helpers, file keyring public API, generated RPC free helpers.

Research notes:
- Add uses relaxed JSON decode; remove uses standard object decode.
