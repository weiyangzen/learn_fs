# File Research: sources/virtualization/spdk/lib/keyring/keyring.c

Implements SPDK's global keyring registry with module-backed key storage, lazy probing, reference counting, removed-key lifetime handling, module initialization/cleanup, and config/introspection helpers.

Key entry points:
- `spdk_keyring_add_key()` registers a key owned by a `spdk_keyring_module` and delegates module-specific storage to `module->add_key()`.
- `spdk_keyring_remove_key()` removes an existing key if it is owned by the requesting module.
- `spdk_keyring_get_key()`, `spdk_keyring_put_key()`, and `spdk_key_dup()` manage references to keys.
- `spdk_key_get_name()`, `spdk_key_get_key()`, `spdk_key_get_ctx()`, and `spdk_key_get_module()` expose key metadata, secret material, module-private context, and ownership.
- `spdk_keyring_for_each_key()` iterates active keys and optionally removed keys.
- `spdk_keyring_register_module()`, `spdk_keyring_init()`, and `spdk_keyring_cleanup()` manage module lifecycle.
- `spdk_keyring_write_config()` and `keyring_dump_key_info()` export module/key metadata to JSON.

Core mechanics:
- The implementation currently supports only a global keyring. Names like `"key0"` and `":key0"` compare as the same global key, while `"ring:key0"` is rejected because named keyrings do not exist.
- Keys live on `g_keyring.keys` while active and move to `g_keyring.removed_keys` after removal if references remain.
- Each `spdk_key` includes inline module-private context immediately after the struct; `spdk_key_get_ctx()` returns `key + 1`.
- `spdk_keyring_get_key()` first searches active keys, then calls each registered module's `probe_key()` callback to lazily instantiate keys not already present.
- Probed keys are automatically removed when the last external reference is dropped and only the keyring's own reference remains.
- Keyring initialization creates a recursive mutex, then initializes registered modules. Modules returning `-ENODEV` are skipped and removed from the module list.
- Cleanup removes all active keys, forcibly frees removed keys that still have references after warning, then calls module cleanup callbacks.

Important invariants:
- All key list and reference count operations are protected by `g_keyring.mutex`.
- `keyring_free_key()` requires `refcnt == 0`.
- Removed keys stay valid until their outstanding references are put.
- A module may only remove keys it owns.
- Active key names must be unique after stripping any leading global-keyring prefix.
- `spdk_key_get_key()` returns `-ENOKEY` for removed keys and otherwise delegates secret retrieval to the owning module.

Filesystem/block relevance:
- This is SPDK's in-process secret registry. Storage stacks that need encryption keys can reference named keys without embedding the key material directly in block-device configuration.

Notable risks:
- `spdk_key_dup()` assumes a non-null key and does not validate removed state.
- `spdk_keyring_register_module()` inserts modules without locking; the intended use is static/early registration before concurrent keyring operations.
- Cleanup forcibly sets leaked removed-key references to zero, which prevents memory leaks at shutdown but can hide caller lifetime bugs.
