# sources/object-store/rustfs/crates/policy/src/policy/principal.rs

## Purpose

Models bucket-policy principals with AWS-compatible JSON handling. It supports wildcard string principals, object-form `AWS` principals, and object-form `Service` principals, and provides principal pattern matching for bucket policy statements.

## Important APIs, Types, and Functions

- `Principal { aws, service }` stores principal patterns as private `HashSet<String>` fields.
- Custom `Serialize` emits only non-empty `AWS`/`Service` fields and uses a single string for singleton sets, otherwise arrays.
- `PrincipalFormat` accepts either a wildcard string or object form.
- `PrincipalObject` uses `deny_unknown_fields` and supports optional `AWS` and `Service`.
- `PrincipalValues` accepts a single string or set of strings.
- `Principal::is_match(principal)` tests both AWS and Service patterns with `wildcard::is_simple_match`.
- `Validator for Principal` rejects empty principal sets.

## Control Flow

Deserialization treats only the literal string `"*"` as valid wildcard string form and maps it to an AWS wildcard. Object form converts provided values into sets and rejects objects that contain neither AWS nor Service. Matching scans AWS patterns first and then service patterns, returning true on the first simple wildcard match.

## State and Persistence

Pure in-memory value object. No persistence or global state.

## Dependencies and Integration Points

Used by `BPStatement` in bucket policy evaluation. Depends on `policy::utils::wildcard` for matching and the common `Validator` trait. Service principal support enables AWS-style bucket policies for service actors such as S3 logging.

## Risks and Edge Cases

- The raw string form accepts only `"*"`, not arbitrary AWS principal strings; non-wildcard principals must use object form.
- Sets mean duplicate principals are collapsed and output order is not stable for multi-element serialization.
- `is_simple_match` has different `?` semantics from strict wildcard matching; this is intentional but should be kept in mind for principal patterns.
- Private fields force tests and construction outside the module to use JSON deserialization or helper constructors.

## Test Signals

Inline tests cover accepted and rejected principal JSON forms, singleton and multi-element serialization, service principal round-trips, service matching, and combined AWS/Service matching.
