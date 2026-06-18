# sources/storage-engines/tikv/components/encryption/src/backup/mod.rs

Purpose: This module file exposes backup encryption support from the encryption crate.

Important APIs and modules: It contains `pub mod backup_encryption;`.

Control flow: No runtime control flow.

State and persistence behavior: No state is defined here.

Dependencies and integration points: It is the namespace entry point for `BackupEncryptionManager`.

Risks: Minimal; adding backup encryption modules requires explicit export here.

Test signals: Compilation verifies the module path.
