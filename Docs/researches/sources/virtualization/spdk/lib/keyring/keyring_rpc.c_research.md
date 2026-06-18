# File Research: sources/virtualization/spdk/lib/keyring/keyring_rpc.c

Adds the JSON-RPC method for listing keyring keys.

Key entry points:
- `rpc_keyring_get_keys()` emits a JSON result array and iterates all active and removed keys with `spdk_keyring_for_each_key(..., SPDK_KEYRING_FOR_EACH_ALL)`.
- `rpc_keyring_for_each_key_cb()` writes one JSON object per key using `keyring_dump_key_info()`.
- `SPDK_RPC_REGISTER("keyring_get_keys", rpc_keyring_get_keys, SPDK_RPC_RUNTIME)` registers the method at runtime.

Core mechanics:
- The RPC takes no decoded parameters in this file.
- Each returned object includes the key info emitted by `keyring_dump_key_info()`: name, module, removed flag, probed flag, refcount, and any module-specific dump fields for active keys.

Filesystem/block relevance:
- This is the management-plane view of SPDK's key registry, useful for inspecting keys that storage components may use for encryption or authentication.

Notable risks:
- The RPC includes removed keys and reference counts, which is helpful for diagnostics but exposes internal lifetime state to callers with RPC access.
