# sources/object-store/rustfs/crates/policy/src/service_type.rs

## Purpose

Defines a small service discriminator for policy-related service names.

## Important APIs, Types, and Functions

- `ServiceType` enum has `S3` and `STS` variants.
- `impl TryFrom<&str> for ServiceType` accepts `"s3"` and `"sts"` and returns `Error::InvalidServiceType` for anything else.

## Control Flow

Conversion is a direct string match with lower-case accepted spellings only.

## State and Persistence

No state beyond the enum value.

## Dependencies and Integration Points

Depends on crate `Error`. Likely used by policy parsing or API code to route service-specific authorization.

## Risks and Edge Cases

- Matching is case-sensitive; `"S3"` or `"STS"` are rejected.
- Only S3 and STS are represented, despite the policy action model also containing Admin and KMS families.

## Test Signals

No local tests in this file. Coverage would come from callers that parse service strings.
