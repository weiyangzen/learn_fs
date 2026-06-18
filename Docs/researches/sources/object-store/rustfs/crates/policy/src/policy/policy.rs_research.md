# sources/object-store/rustfs/crates/policy/src/policy/policy.rs

## Purpose

Defines the top-level IAM and bucket policy data models, request argument structs, policy validation, policy merging, default built-in policies, claim-policy extraction helpers, and ExistingObjectTag prefetch analysis. It is the aggregation layer that applies statement-level authorization decisions into complete allow/deny policy semantics.

## Important APIs, Types, and Functions

- `DEFAULT_VERSION = "2012-10-17"` is the accepted IAM policy version.
- `Validator` is the shared validation trait used by policy model types.
- `Args<'a>` carries identity-policy request context: account, groups, action, bucket, object, conditions, claims, owner flag, and `deny_only`.
- `Args::get_role_arn()` and `Args::get_policies()` expose claim-derived role/policy values.
- `Policy { id, version, statements }` represents identity policy JSON.
- `Policy::is_allowed(args)` implements deny-first, deny-only, owner, and allow-statement evaluation.
- `Policy::match_resource(resource)` tests whether any statement resource matches a resource string.
- `Policy::merge_policies(inputs)` concatenates statements and removes duplicates.
- `Policy::parse_config(data)` deserializes JSON and validates it.
- `BucketPolicyArgs<'a>` is the bucket-policy request context without claims and deny-only.
- `BucketPolicy { id, version, statements }` represents bucket policy JSON.
- `BucketPolicy::is_allowed(args)` mirrors deny-first then owner then allow semantics for `BPStatement`.
- `get_policies_from_claims`, `iam_policy_claim_name_sa`, and internal `get_values_from_claims` parse policy names from string or array claims, splitting comma-delimited entries.
- `policy_uses_existing_object_tag_conditions`, `bucket_policy_uses_existing_object_tag_conditions`, and request-narrowing variants detect when object tags may be needed to evaluate conditions.
- `default::DEFAULT_POLICIES` defines `readwrite`, `readonly`, `writeonly`, `diagnostics`, and `consoleAdmin` built-in policies.

## Control Flow

`Policy::is_allowed` evaluates all explicit deny statements first. A matching deny is represented by `Statement::is_allowed` returning false after deny effect inversion, so the policy immediately rejects. If `deny_only` is set and no deny matched, the request is allowed without evaluating allow statements. Otherwise owners are allowed, then allow statements are scanned until one returns true. If none match, the default result is deny.

`BucketPolicy::is_allowed` follows the same deny-first pattern, then owner override, then allow scan. There is no deny-only path for bucket policies.

Validation enforces the default version when a version is present and delegates statement validation. Policy merging preserves the first non-empty version from inputs, appends all statements, then removes duplicates using statement equality that intentionally ignores SID.

Claim extraction first looks up claim names using exact-match preference and case-insensitive fallback from `get_claim_case_insensitive`. Ambiguous case-insensitive matches are treated as missing. String and array claims are split on commas and trimmed into a set.

ExistingObjectTag analysis first serializes `Functions` to JSON and searches keys recursively for `ExistingObjectTag`/`s3:ExistingObjectTag` forms. Request-specific helpers then use statement `request_reaches_condition_eval` to avoid fetching object tags when action, principal, or resource would skip the tag-dependent statement.

## State and Persistence

Policies and default policies are in-memory structures. `DEFAULT_POLICIES` uses `LazyLock` for process-local lazy initialization. No file or database persistence occurs in this file.

## Dependencies and Integration Points

Integrates with `Statement`, `BPStatement`, action/resource/function/effect/ID types, claim lookup utilities, `serde_json::Value`, and `rustfs_credentials::IAM_POLICY_CLAIM_NAME_SA`. Default policies depend on action enums for S3, STS, Admin, and KMS. Runtime callers supply `Args` or `BucketPolicyArgs` from S3/API authorization paths.

## Risks and Edge Cases

- `deny_only` intentionally allows requests if no explicit deny matches, even if no allow matches; callers must only use it for deny-only validation.
- Owner override occurs after denies, so explicit denies still block owner requests; this is security-sensitive and covered by tests.
- `Policy::merge_policies` de-duplicates based on statement equality that ignores SID and `not_resources`; equality includes effect, actions, not_actions, resources, and conditions only via `Statement::eq`, so duplicate semantics should be reviewed when NotResource is involved.
- Empty `{}` identity policy parses as an implied empty policy with no statements.
- ExistingObjectTag detection serializes conditions to JSON; serde shape changes in condition types can affect detection.
- Default policy definitions are authorization-critical and should stay aligned with action enum behavior.

## Test Signals

Inline tests cover parsing, single-string Action/Resource compatibility, default policy validity and STS allow, deny-only semantics, ListBucket prefix/resource behavior, bucket policy ListBucket behavior, policy variable substitution including nested and multi-value variables, NotAction/NotResource validation, admin/table resource scoping, STS/KMS/Admin resource exceptions, mixed action family rejection, serialization omission and deterministic order, ExistingObjectTag detection and request narrowing, claim lookup ambiguity, and JSON round trips.
