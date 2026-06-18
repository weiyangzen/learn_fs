# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_crypt.c

## Purpose

Manages ZFS native encryption state in the DSL and SPA keystore. It handles wrapping keys, decrypted DSL crypto keys, dataset-to-key mappings, key load/unload/change-key workflows, encryption-root inheritance, clone/promote/rename constraints, encrypted dataset creation, raw encrypted receive/send key nvlists, key ZAP object lifecycle, keystatus/stat reporting, and block/object-set encryption MAC operations.

## Main Entry Points

- Crypto parameter handling: `dsl_crypto_params_create_nvlist()`, `dsl_crypto_params_free()`.
- Keystore lifecycle: `spa_keystore_init()`, `spa_keystore_fini()`.
- Wrapping-key operations: `spa_keystore_load_wkey()`, `spa_keystore_unload_wkey()`, `spa_keystore_load_wkey_impl()`, `spa_keystore_unload_wkey_impl()`.
- Key mapping operations: `spa_keystore_create_mapping()`, `spa_keystore_remove_mapping()`, `spa_keystore_lookup_key()`, `key_mapping_add_ref()`, `key_mapping_rele()`.
- Key changes: `spa_keystore_change_key_check()`, `spa_keystore_change_key_sync()`, `spa_keystore_change_key()`.
- Dataset rules: `dsl_crypto_can_set_keylocation()`, `dsl_dir_rename_crypt_check()`, `dsl_dataset_promote_crypt_check()`, `dsl_dataset_promote_crypt_sync()`, `dmu_objset_create_crypt_check()`, `dsl_dataset_create_crypt_sync()`.
- Raw receive/send: `dsl_crypto_recv_raw()`, `dsl_crypto_recv_key_check()`, `dsl_crypto_recv_key_sync()`, `dsl_crypto_recv_raw_objset_check()`, `dsl_crypto_recv_raw_objset_sync()`, `dsl_crypto_recv_raw_key_check()`, `dsl_crypto_recv_raw_key_sync()`, `dsl_crypto_populate_key_nvlist()`.
- DSL key objects and crypto operations: `dsl_crypto_key_create_sync()`, `dsl_crypto_key_clone_sync()`, `dsl_crypto_key_destroy_sync()`, `dsl_dataset_crypt_stats()`, `spa_crypt_get_salt()`, `spa_do_crypt_objset_mac_abd()`, `spa_do_crypt_mac_abd()`, `spa_do_crypt_abd()`.

## Control Flow And State

The SPA keystore has three AVL trees guarded by separate rwlocks: loaded wrapping keys keyed by encryption-root dsl_dir object, decrypted DSL crypto keys keyed by key ZAP object, and dataset-object mappings to crypto keys. Wrapping keys represent user-supplied keys and carry keyformat/salt/iters metadata. DSL crypto keys hold unwrapped master/HMAC key material and reference their wrapping key. Dataset mappings let ZIO/ARC look up a loaded key by objset id during I/O.

`dsl_crypto_params_create_nvlist()` parses encryption properties and ioctl crypto arguments, validates crypt/keyformat/keylocation/wrapping-key length, normalizes `encryption=on`, creates a wrapping key when raw key data is supplied, and removes encryption-only properties from the ordinary DSL property nvlist. Free paths zero and release key buffers when ownership is transferred with `unload`.

Loading a key validates the supplied wrapping key by opening and unwrapping the on-disk DSL crypto key ZAP, then initializes keyformat/salt/iters from disk and inserts the wrapping key. Unloading waits for txg I/O to finish, then removes a wrapping key only if its refcount is zero. Opening a DSL crypto key reads crypt suite, GUID, encrypted master key, encrypted HMAC key, IV, MAC, and optional version from the key ZAP, unwraps through `zio_crypt_key_unwrap()`, and caches the result.

Change-key sync recurses through children and clone references with `spa_keystore_change_key_sync_impl()`. It either rewrites the recorded encryption root object or rewraps each affected DSL crypto key with a new wrapping key. Forced variants update encryption-root metadata without requiring loaded keys. Normal variants require relevant keys loaded so data remains accessible and wrapped correctly.

Dataset creation either inherits a parent's wrapping key or creates a new encryption root. Clones share the origin's key object by incrementing the key ZAP refcount. Promotion can move encryption-root identity from origin to target when safe, copying keylocation and updating descendant crypto key root references. Rename checks prevent moving non-root encrypted datasets under a different encryption root.

Raw encrypted receive validates metadnode geometry, portable MAC, raw key nvlist fields, key version, keyformat/PBKDF2 consistency, and IV-set GUID continuity for incrementals unless `zfs_disable_ivset_guid_check` is set. Sync can create or update a raw objset, set raw write flags and object-set MACs, write raw key material exactly as provided, and activate encryption. `dsl_crypto_populate_key_nvlist()` exports the raw key ZAP fields plus metadnode properties and from/to IV-set GUIDs for raw send.

The bottom crypto helpers perform salt lookup, object-set MAC generation/verification, generic data MAC generation/verification, and encryption/decryption dispatch. `spa_do_crypt_abd()` borrows ABD buffers, obtains the dataset key mapping, generates random or dedup-derived salt/IV when encrypting, calls `zio_do_crypt_data()`, handles decryption fault injection except for dnode blocks, and carefully returns ABD buffers and key references on both success and error.

## Dependencies

Depends on DSL dataset/dir structures, MOS ZAP key objects, DSL properties, sync tasks, SPA feature flags, txg synchronization, zio crypto primitives, ABD buffer APIs, objset physical MAC fields, zvol hooks, raw receive machinery, nvlist helpers, and zfs_refcount/AVL/rwlock primitives.

## Risks

This file protects key material and must maintain exact reference lifetimes across three trees. Lock ordering around `sk_wkeys_lock`, `sk_dk_lock`, and `sk_km_lock` matters because I/O paths perform key lookup under reader locks. Key changes recurse through dataset trees and clone lists, so missed descendants would leave stale wrapping-root metadata. Raw receive is compatibility-sensitive: IV-set GUID checks, key version checks, metadnode geometry, and portable MACs must match send-side expectations. Error paths must zero generated salt/IV/MAC state and return ABD buffers correctly. The raw objset check contains a duplicated IV-set GUID validation block, which is behaviorally redundant but worth noting for maintenance.
