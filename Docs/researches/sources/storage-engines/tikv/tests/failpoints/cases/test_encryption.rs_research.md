# sources/storage-engines/tikv/tests/failpoints/cases/test_encryption.rs

Purpose: tests encryption metadata recovery and KMS temporary-unavailable retry behavior.

Important APIs and functions: `test_file_dict_file_record_corrupted` uses `FileDictionaryFile`, `create_file_info`, and failpoint `file_dict_log_append_incomplete`. `test_kms_provider_temporary_unavailable` uses fake KMS helpers and failpoints `kms_api_timeout_encrypt` and `kms_api_timeout_decrypt`.

Control flow: first test truncates an intermediate log record and expects recovery failure, then truncates the final record and expects recovery to keep prior entries. Second test injects one timeout on encrypt and decrypt and expects retry success.

State and persistence: file dictionary log records are persisted in tempdir; recovery must distinguish unrecoverable middle corruption from discardable tail corruption. KMS backend state is cleared between encrypt/decrypt phases.

Dependencies and integration: uses encryption crate, encryption protobufs, tempfile, and fail-rs.

Risks and test signals: corruption byte count assumes record header layout. Signals protect encrypted file metadata durability and transient KMS tolerance.
