<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/common.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/kms/common.rs

Purpose: this is the shared support library for RustFS KMS E2E tests. It manages local and Vault KMS test environments, admin KMS API calls, key-file creation, common SSE-S3/SSE-KMS/SSE-C assertions, multipart encryption workflows, and utility constants.

Important APIs, types, and functions: constants define `TEST_BUCKET`, Vault address/token/transit path/default key, and `RUSTFS_TEST_VAULT_BIN`. Admin helpers include `configure_kms()`, `start_kms()`, `get_kms_status()`, `create_default_key()`, and `test_kms_key_management()`. Encryption helpers include `sse_customer_key_md5_base64()`, `test_sse_c_encryption()`, `test_sse_s3_encryption()`, `test_sse_kms_encryption()`, `test_error_scenarios()`, `EncryptionType`, `MultipartTestConfig`, `test_multipart_upload_with_config()`, `create_sse_c_config()`, and `test_all_multipart_encryption_types()`. Environment types are `VaultTestEnvironment` and `LocalKMSTestEnvironment`.

Control flow: local KMS tests create a temp key directory, write a JSON `.key` file with generated AES-256 material, and start RustFS with `--kms-enable --kms-backend local --kms-key-dir --kms-default-key-id`. Vault tests spawn `vault server -dev`, wait for TCP plus health readiness, enable transit, create the transit key, start RustFS, configure the Vault backend via admin API, and start KMS. Multipart helper builds deterministic data, creates an upload with the selected encryption mode, uploads all parts with SSE-C headers when needed, completes the upload, downloads it, checks encryption headers, and byte-compares content.

State and persistence: persistent test state is local KMS key JSON under the environment temp directory, spawned Vault process state, RustFS KMS runtime configuration, bucket/object metadata, multipart upload IDs and ETags, and customer key/MD5 values. `VaultTestEnvironment::drop()` kills the Vault child process.

Dependencies and integration points: depends on `crate::common` awscurl and HTTP helpers, `aws_sdk_s3`, `base64`, `md5`, `rand`, `chrono`, `tokio::fs`, `reqwest`, a Vault binary when Vault tests are run, and RustFS admin KMS endpoints.

Risks: local key-file format is manually constructed and coupled to backend internals. Vault uses a hard-coded dev token and fixed port, so parallel runs conflict. Several helpers skip when `awscurl` is absent, hiding KMS admin coverage in normal environments. Fixed sleeps and readiness loops may be flaky under load. Log strings include non-ASCII symbols while most source is ASCII.

Test signals: this file enables most KMS coverage; signals include successful KMS configure/start/status, create/describe/list keys, correct SSE headers, wrong SSE-C key rejection, Vault process readiness, multipart data integrity across encryption modes, and environment cleanup through process termination.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/kms/common.rs -->
