# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_azure.rs

## Purpose

Azure warm-tier adapter using the transition-client S3-compatible abstraction.

## Important APIs and Types

`WarmBackendAzure(WarmBackendS3)`, constructor, `WarmBackend` impl, and shared multipart sizing helper.

## Control Flow

Validates access/secret keys and bucket, parses endpoint, creates Signature V4 credentials, enables trailing headers and DNS bucket lookup, builds provider id `"azure"`, wraps S3 backend, and delegates reads/removes/listing. Upload sets part size and disables content SHA256.

## State and Persistence Behavior

No durable local state; remote bucket/prefix stores tiered data.

## Dependencies and Integration Points

Uses `TierAzure`, transition API types, `WarmBackendS3`, and shared put-option conversion; selected for `TierType::Azure`.

## Risks and Edge Cases

Azure service-principal fields exist in config but are not used here. Azure-native semantics are delegated to S3-compatible transition behavior. No tests validate endpoint/auth behavior.

## Test Signals

No direct tests; should cover SP expectations, credentials, endpoint parsing, part sizing, and remote CRUD.
