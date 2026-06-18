# sources/storage-engines/tikv/components/cloud/aws/src/kms.rs

## Purpose
This file implements the shared `cloud::kms::KmsProvider` trait for AWS KMS. It creates an AWS KMS client from TiKV cloud KMS config, supports either explicit AWS access keys or the default credential chain, generates AES-256 data keys, decrypts encrypted data keys, and maps AWS SDK failures into TiKV cloud error categories.

## Important APIs, Types, And Functions
`AwsKms` stores an `aws_sdk_kms::Client`, current `KeyId`, region, and endpoint. `ENCRYPTION_VENDOR_NAME_AWS_KMS` returns the provider name `"AWS"`. `new` constructs the provider using a shared HTTP client and either static credentials from `config.aws` or `util::DefaultCredentialsProvider`. `new_with_creds_client` is the injectable constructor used by tests.

The `KmsProvider` implementation exposes `name`, `decrypt_data_key`, and `generate_data_key`. `generate_data_key` calls AWS `GenerateDataKey` with `DataKeySpec::Aes256` and returns `DataKeyPair { encrypted, plaintext }`, validating plaintext as `CryptographyType::AesGcm256`. `decrypt_data_key` calls AWS `Decrypt` with the configured key ID and ciphertext blob.

Error translation is handled by `classify_generate_data_key_error`, `classify_decrypt_error`, and `classify_error`. Service errors such as not found, incorrect key, timeout, and internal errors become `ApiNotFound`, `WrongMasterKey`, `ApiTimeout`, `ApiInternal`, or generic `KmsError::Other`. Dispatch failures sourced from `CredentialsError` become `ApiAuthentication`; other dispatch failures become `ApiTimeout`; retryable SDK errors become `ApiInternal`.

## Control Flow
Construction starts from `aws_config::defaults(BehaviorVersion::latest())`, installs credentials and HTTP client, applies region and endpoint via `util`, synchronously waits for config loading through `block_on`, and builds the KMS client. Runtime operations are async KMS SDK calls followed by immediate error classification and response field extraction. The code assumes successful AWS responses contain `plaintext`/`ciphertext_blob` and unwraps those fields.

## State And Persistence Behavior
`AwsKms` is stateless apart from the configured client, key ID, region, and endpoint. It does not persist keys locally. Generated plaintext keys are returned to callers in memory, while encrypted keys are AWS ciphertext blobs suitable for persistence by higher layers. There is no local retry loop in KMS operations; retry classification is used to choose TiKV error categories, while AWS SDK retry behavior depends on SDK config.

## Dependencies And Integration Points
The file integrates AWS KMS SDK types, shared AWS util helpers, `cloud::kms` abstractions, TiKV cloud errors, and AWS credential provider traits. Tests use Smithy `StaticReplayClient` to verify request bodies and mocked JSON responses. The public re-export from `lib.rs` makes `AwsKms` the AWS KMS provider surface for the crate.

## Risks
Successful responses unwrap optional AWS fields, so malformed or partial SDK responses panic rather than returning an error. Credential-error detection reaches through dispatch connector error sources and may miss new SDK error wrapping. Wrong-master-key classification intentionally treats KMS `NotFoundException` during decrypt as `WrongMasterKey`, which is correct for restore safety but conflates missing key and incorrect key from an operator perspective.

## Test Signals
`test_aws_kms` verifies generate/decrypt requests with a static replay KMS client and validates encrypted/plaintext key content. `test_kms_wrong_key_id` verifies `IncorrectKeyException` maps to `KmsError::WrongMasterKey`. A localstack test exists but is ignored because no reliable AWS KMS backend is available in the normal test environment.
