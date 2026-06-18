# sources/object-store/rustfs/crates/policy/src/policy/resource.rs

## Purpose

Defines policy resources and resource sets, including AWS S3 ARN parsing/serialization, validation, wildcard resource matching, condition-variable substitution, and policy-variable expansion. It is the resource authorization primitive used by statements.

## Important APIs, Types, and Functions

- `ResourceSet(pub Vec<Resource>)` preserves input order while providing duplicate suppression during deserialization.
- `ResourceSet::is_match(...)` and `is_match_with_resolver(...)` match any resource in the set against a request resource.
- `ResourceSet::match_resource(resource)` matches without conditions.
- `ResourceSet` custom serde accepts either a string or array and serializes as an array of resource strings.
- `Resource` has variants `S3(String)` and `Kms(String)`, although `TryFrom<&str>` currently accepts only S3 ARNs.
- `Resource::S3_PREFIX` is `arn:aws:s3:::`.
- `Resource::is_match_with_resolver(...)` expands variables, substitutes common condition keys, path-cleans the request resource, and checks exact or wildcard match.
- `Validator for Resource` rejects empty S3 resources, S3 resources starting with `/`, and KMS values containing path-like characters.

## Control Flow

Deserialization parses each resource string through `Resource::try_from`, strips the S3 ARN prefix, validates, and pushes only unique values. Matching expands the stored pattern through a `PolicyVariableResolver` when present. For each expanded pattern, it replaces common key variables with the first non-empty request condition value. It then normalizes the incoming request resource through `path::clean`; a non-dot exact equality succeeds, otherwise wildcard matching is attempted.

## State and Persistence

Resource objects hold only strings in memory. There is no persistence.

## Dependencies and Integration Points

Used by `Statement`, `BPStatement`, top-level policy matching, and default policies. Depends on `KeyName::COMMON_KEYS`, `policy::variables::resolve_aws_variables`, `policy::utils::path::clean`, and `policy::utils::wildcard`. It is part of the defense against path traversal-like resource matching bypasses.

## Risks and Edge Cases

- KMS resources exist as an enum variant but are not parsed from strings by `TryFrom<&str>`, so external JSON KMS resource support is incomplete or intentionally unused.
- Matching rejects cleaned `"."`, preventing empty/dot request resources from matching.
- Path cleaning can change request resource strings before wildcard matching; this is security-friendly for traversal but may differ from byte-exact S3 key semantics if callers pass keys containing dot segments.
- Serialization always emits ResourceSet as an array, even if source JSON was a single string.

## Test Signals

Inline tests cover broad S3 resource wildcard matching, bucket vs object resources, `?` matching, negative bucket/object cases, and path traversal defenses for `../` and nested safe/../../ patterns.
