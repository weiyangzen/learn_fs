# sources/storage-engines/tikv/components/encryption/src/lib.rs

Purpose: Crate root for TiKV encryption. It wires internal modules, re-exports the public API, and provides directory deletion helpers that keep encryption metadata consistent with filesystem cleanup.

Important APIs and types: Re-exports include config, `AesGcmCrypter`, `FileEncryptionInfo`, `Iv`, `EncryptedFile`, `Error`, `FileDictionaryFile`, stream wrappers, `DataKeyManager`, `DataKeyImporter`, and master-key backends. Public helpers are `trash_dir_all`, `clean_up_trash`, and `clean_up_dir`.

Control flow: `trash_dir_all` renames a directory to `TRASH-<name>`, asks the key manager to remove metadata using the original logical path and trash physical path, then removes the trash directory. `clean_up_trash` resumes deletions for leftover trash directories after restart. `clean_up_dir` deletes all direct child directories with a prefix and optionally removes metadata.

State and persistence behavior: State changes are delegated to `DataKeyManager::remove_dir`, so dictionary entries are removed before physical recursive delete completes. The trash prefix gives crash recovery a durable marker for deletion-in-progress.

Dependencies and integration: Used by storage cleanup paths that need directory removal while encryption is enabled. It integrates file-system operations with key manager metadata and exports test utilities for dependent crates.

Risks: Directory names are converted through `to_str().unwrap()` in cleanup paths, so non-UTF-8 names can panic. Existing trash-name collisions are left to filesystem rename behavior. Metadata removal and physical removal remain separate operations, but `clean_up_trash` is designed to repair restart leftovers.

Test signals: Root tests cover basic trash deletion, deletion with pre-existing trash path, cleanup of restart leftovers, and prefix cleanup without an encryption manager. Manager tests additionally cover encrypted trash-dir cleanup.
