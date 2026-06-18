# sources/object-store/garage/src/garage/tests/common/mod.rs

Purpose: This module ties the integration-test harness together. It exposes shared modules, test region, `Context`, K2V-specific context, and helper methods for creating buckets and clients.

Important APIs and types: `Context` contains the static `garage::Instance`, current key, AWS S3 client, custom S3 requester, and optional `K2VContext`. `K2VContext` wraps a custom requester. `context()` creates a fresh `Context` view over the singleton instance. `Context::create_bucket` and `Context::k2v_client` are the main helper methods.

Control flow: `Context::new` retrieves the singleton Garage instance, creates a fresh key, builds an AWS SDK client, creates custom S3 and optional K2V requesters, and returns the context. `create_bucket` runs CLI `bucket create` and `bucket allow --owner --read --write` for the current key. `k2v_client` builds a typed `K2vClient` against the K2V endpoint.

State and persistence behavior: Context construction can create new access keys. `create_bucket` persists bucket metadata and permissions. The module itself holds only lightweight references and clients.

Dependencies and integration points: It integrates the AWS SDK, custom request signer, Garage process harness, CLI helpers, optional K2V client crate, and shared region `garage-integ-test`. All integration test modules depend on it.

Risks: `create_bucket` uses the exact provided name without adding a random suffix despite the comment, so tests must use unique names. Each call to `context()` creates a new key, which is useful for isolation but can leave many keys in the test metadata. Optional K2V fields are gated by the `k2v` feature.

Test signals: Successful bucket creation and permission grants in nearly every test validate this module's integration wiring.
