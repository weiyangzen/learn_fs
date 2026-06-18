# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_crypt.h

Read status: complete, 235 lines.

Purpose: DSL encryption key management and SPA keystore interface.

Key structures and APIs:
- On-disk crypto key ZAP names include suite, GUID, IV, MAC, master key, HMAC key, root dsl_dir object, refcount, and version.
- `dsl_wrapping_key_t` stores loaded wrapping key state for an encryption root: keyformat, PBKDF2 salt/iters, crypto key, refcount, and owning dsl_dir object.
- `dcp_cmd_t` describes crypto parameter commands for raw receive, new key, inherit, and forced variants.
- `dsl_crypto_params_t` packages command, encryption algorithm, keylocation, and wrapping key.
- `dsl_crypto_key_t` stores a loaded DSL crypto key: holds, derived encryption key, wrapping key, and on-disk object.
- `dsl_key_mapping_t` maps dataset object id to DSL crypto key for zio-layer encryption/decryption lookup.
- `spa_keystore_t` owns AVL trees and locks for DSL keys, dataset mappings, and wrapping keys.
- APIs cover crypto param creation/free, dataset crypto stats, keylocation validation, keystore init/fini, wrapping key load/unload, key mapping create/remove/ref/release/lookup, raw receive key population/check/sync, change-key check/sync, rename/promote crypto checks, encrypted objset create checks/sync, key create/clone/destroy, salt lookup, MAC generation/verification, objset MAC, and data encrypt/decrypt via ABD.

Dependencies: DMU transactions, DMU object types, ZIO crypt, SPA, DSL dataset/dir.

Research notes:
- The header captures both administrative key lifecycle and data-path cryptographic entry points.
- Dataset object ids are the bridge between DSL key mapping and zio block encryption.
