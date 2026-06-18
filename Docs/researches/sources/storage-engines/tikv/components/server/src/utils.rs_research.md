# sources/storage-engines/tikv/components/server/src/utils.rs

Purpose: small server helper for constructing backup encryption manager state used by backup stream setup.

Important APIs and functions: `build_backup_encryption_manager` accepts an optional `Arc<DataKeyManager>` and returns `BackupEncryptionManager` configured with no explicit backend, plaintext method, a new `MultiMasterKeyBackend`, and the optional data key manager.

Control flow: the function is a straight constructor wrapper returning `io::Result`, currently without fallible operations beyond the wrapped type contract.

State and persistence behavior: no direct persistence. It passes through the server encryption key manager so backup/log-backup paths can resolve file encryption metadata consistently.

Dependencies and integration points: used by `server2.rs` while starting backup stream. Depends on `encryption::{BackupEncryptionManager, DataKeyManager, MultiMasterKeyBackend}` and `kvproto::encryptionpb::EncryptionMethod`.

Risks: hard-coded plaintext method means actual encryption behavior depends on the optional data key manager and backup manager semantics. Future backup encryption changes should revisit this constructor instead of duplicating manager setup.

Test signals: no direct tests.
