<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_vault_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/kms_vault_test.rs

Purpose: this module mirrors KMS E2E coverage against a Vault Transit backend. It validates Vault bootstrap, RustFS KMS configuration/startup, encryption modes, multipart behavior, key isolation, and Vault-backed key CRUD semantics.

Important APIs, types, and functions: `VaultKmsTestContext` wraps `VaultTestEnvironment` and exposes `base_env()` and `s3_client()`. Tests use shared helpers `get_kms_status()`, `start_kms()`, `test_kms_key_management()`, `test_sse_c_encryption()`, `test_sse_s3_encryption()`, `test_sse_kms_encryption()`, `test_error_scenarios()`, `test_all_multipart_encryption_types()`, and `sse_customer_key_md5_base64()`. `test_vault_kms_key_crud()` directly calls admin KMS key create/describe/list/delete endpoints.

Control flow: context creation starts a dev Vault process, enables transit, creates the default transit key, starts RustFS, configures Vault Transit KMS, starts the KMS service, and waits briefly. The end-to-end test checks status, creates a bucket, runs key management plus SSE-C/SSE-S3/SSE-KMS/error helpers, and deletes the bucket. Other tests cover SSE-C key isolation, 1 MiB SSE-S3 upload/download, all multipart encryption types, and CRUD including tag preservation, pending-deletion state, force delete, and final not-found behavior.

State and persistence: state spans a child Vault dev process, Vault transit mount/key state, RustFS KMS config, temporary bucket/object data, KMS key metadata/tags/deletion state, and SSE-C keys. The Vault process is killed by `VaultTestEnvironment::drop()`.

Dependencies and integration points: requires a Vault binary (`vault` or `RUSTFS_TEST_VAULT_BIN`), fixed localhost port 8200, awscurl for admin calls, RustFS Vault Transit backend support, AWS SDK S3, and serial execution.

Risks: fixed Vault port and dev token prevent parallel Vault tests. Tests skip when awscurl is absent but not when Vault is absent; missing Vault fails context setup. Fixed sleeps may be insufficient under slow startup. Key CRUD asserts exact response shape and state names, which is valuable but tightly coupled to admin API schema.

Test signals: passing tests show Vault Transit can be configured and started, KMS status is queryable, encryption modes work over Vault-backed keys, SSE-C isolation remains enforced, multipart encryption works across modes, key tags survive create/list/describe, delete transitions to `PendingDeletion`, and force delete removes the key.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/kms_vault_test.rs -->
