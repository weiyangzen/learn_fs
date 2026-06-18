## sources/security-integrity/cryfs/crates/cli-utils/src/blockstore_setup.rs

Purpose: builds the CryFS blockstore stack around a low-level blockstore using config-selected encryption and integrity settings.

Important APIs and types: `BlockstoreCallback` abstracts work performed after stack construction. `setup_blockstore_stack` performs cipher lookup, key parsing, `EncryptedBlockStore` creation, `IntegrityBlockStore` initialization, and wrapping in `LockingBlockStore`. `setup_blockstore_stack_dyn` returns a dynamic `LockingBlockStore<DynBlockStore>` using `DynCallback`.

Control flow and state: cipher lookup invokes `CipherCallbackForBlockstoreSetup`. The callback parses the hex encryption key, constructs the cipher, computes the local integrity state path under the filesystem id, initializes integrity storage with `my_client_id` and `IntegrityConfig`, then calls the user callback. On key/cipher/local-state errors, it async-drops partially built stores before returning a mapped `CliError`.

Dependencies and integration: integrates `cryfs_config` ciphers and `CryConfig`, `cryfs_crypto` key/cipher types, `cryfs_blockstore` encrypted/integrity/locking layers, local state, and CLI error mapping. The check fixture uses `setup_blockstore_stack_dyn`.

Risks and test signals: this is security-critical because wrong key parsing, local integrity state path handling, or integrity-init error mapping can alter filesystem safety. It maps previous integrity violations to specific CLI error kinds, preserving user-visible safety semantics.
