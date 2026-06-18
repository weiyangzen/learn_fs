# sources/storage-engines/tikv/components/cloud/aws/src/util.rs

## Purpose
This module provides private AWS SDK plumbing shared by the AWS S3 and KMS implementations: HTTP client construction, default credential and region providers, retryability classification, endpoint/region configuration helpers, and a retry wrapper that records TiKV cloud error metrics.

## Important APIs, Types, And Functions
`new_http_client` builds a Smithy shared HTTP client backed by Hyper 0.14 and `hyper_tls::HttpsConnector`. `new_credentials_provider` constructs `DefaultCredentialsProvider`, using the current Tokio runtime with `block_in_place` if present or TiKV's external-IO blocking helper otherwise. `is_retryable` classifies AWS `SdkError` variants: timeout, dispatch failure, response/service 5xx, and HTTP 408 are retryable; construction failures and normal 4xx are not.

`configure_endpoint` applies a non-empty endpoint URL to an AWS config loader. `configure_region` either uses an explicit region or installs `DefaultRegionProvider`, whose chain checks environment variables, then AWS profile files, then defaults to `us-east-1`. `retry_and_count` wraps an async action in TiKV `retry_ext`, logs failures with a UUID/context string, and increments `CLOUD_ERROR_VEC` with provider `aws`.

`DefaultCredentialsProvider` wraps AWS `DefaultCredentialsChain`. Its `ProvideCredentials` implementation retries all provider errors through `retry_and_count` and normalizes the final error into a `CredentialsError::provider_error` with a message that includes the underlying source string.

## Control Flow
Credential construction is async internally but exposed through a synchronous function for the provider constructors. At credential lookup time, the provider calls the AWS default chain inside the retry wrapper. If the `cred_err` failpoint is enabled in tests, the provider injects a retryable wrapped credentials error before the real chain call. After retries are exhausted, it rewrites the error message to "Couldn't find AWS credentials in sources (...)".

## State And Persistence Behavior
The module has no durable state. Runtime state includes the AWS default credential chain, region provider chain, HTTP client handles, and Prometheus metric counters incremented on retry failures. The retry wrapper creates a UUID per operation to correlate warning logs.

## Dependencies And Integration Points
Both `kms.rs` and `s3.rs` use these helpers for consistent AWS config loading and retry classification. The module integrates AWS config providers, Smithy runtime error types, Hyper/TLS transport, TiKV retry utilities, TiKV metrics, and failpoints. `SdkError` is aliased to the Smithy orchestrator result type used throughout the AWS crate.

## Risks
All credential provider errors are treated as retryable because the code cannot distinguish their exact causes. This can delay permanent misconfiguration failures. `is_retryable` is HTTP-status based for response/service errors and may miss AWS modeled retry traits. `new_credentials_provider` blocks on async setup and must be used carefully inside Tokio runtimes; it uses `block_in_place` to avoid deadlocks in supported contexts.

## Test Signals
Tests cover retryability for response and service 5xx, 4xx, 408, timeout errors, and construction failures. With the `failpoints` feature, `test_default_provider` injects credential errors and verifies the normalized provider error message.
