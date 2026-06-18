# sources/storage-engines/tikv/components/encryption/src/manager/mod.rs

Purpose: Implements TiKV data-key management for encrypted files. It loads and persists key/file dictionaries, rotates data keys, wraps file readers and writers, tracks metadata for create/link/rename/delete operations, and imports external data keys for restore.

Important APIs and types: `DataKeyManager::new`, `create_file_for_write`, `open_file_with_writer`, `open_file_for_read`, `get_file`, `new_file`, `delete_file`, `link_file`, `rename_file`, `remove_dir`, `dump_key_dict`, and `dump_file_dict` are the main APIs. `Dicts` owns the shared dictionaries and persistence handles. `DataKeyManagerArgs` maps config to runtime arguments. `DataKeyImporter` is an RAII importer with `add`, `commit`, and `rollback`. Internal `RotateTask` coordinates background saving and termination.

Control flow: Startup loads dictionaries with the current master key. If decryption fails with `WrongMasterKey`, it loads with the previous key and rewrites `key.dict` under the current key. If encryption is enabled for the first time, it creates empty dictionaries and immediately rotates a data key. A background thread periodically calls `maybe_rotate_data_key`; rotation also occurs when method changes, the current key exceeds the rotation period, or an exposed key can be replaced under a secure backend.

State and persistence behavior: `file.dict` is plaintext metadata persisted through `FileDictionaryFile`; `key.dict` is encrypted by the master-key backend via `EncryptedFile`. `current_key_id` is atomic so readers avoid partially updated `KeyDictionary.current_key_id`. File metadata operations update in-memory state and append/rewrite file dictionary records with sync on operation boundaries. Key dictionary writes mark keys exposed when saved with insecure master keys.

Dependencies and integration: Integrates with `EncryptionConfig`, stream wrappers from `io.rs`, `EncryptedFile`, master-key `Backend`, protobuf dictionaries, failpoints, metrics, `file_system`, and `walkdir`. RocksDB uses plaintext fallback from `get_file` when a file is not tracked.

Risks: Filesystem changes and dictionary changes are not atomic; code has explicit stale-entry cleanup for link targets and trash-directory workflows to mitigate this. Directory deletion/linking rejects symlinks. Background rotation uses `expect`, so persistent key-dictionary save errors panic the worker. Import rollback only removes imported keys within a time window to avoid deleting keys that may now be shared.

Test signals: Extensive tests cover enable/disable, insecure master rejection, master-key rotation fallback and failure, missing dictionaries, create/get/delete, link/rename, data-key rotation, persistence, exposed-key rotation, plaintext file wrappers, algorithm switches, directory rename/delete, key import rollback/commit, duplicate import races, and encrypted trash cleanup.
