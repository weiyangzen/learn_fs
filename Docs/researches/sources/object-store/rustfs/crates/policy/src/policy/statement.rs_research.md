# sources/object-store/rustfs/crates/policy/src/policy/statement.rs

## Purpose

Defines identity policy statements and bucket policy statements, including serde shape, validation rules, request applicability checks, condition evaluation entry points, resource construction, and effect application.

## Important APIs, Types, and Functions

- `Statement` represents IAM identity statements with `Sid`, `Effect`, `Action`, `NotAction`, `Resource`, `NotResource`, and `Condition`.
- `BPStatement` is the bucket-policy equivalent and adds required `Principal`.
- `variable_resolver_for_policy_args(args)` builds a `VariableResolver` from request claims, account, and conditions.
- `build_resource(action, bucket, object, bucket_resource_only)` creates the resource string used for matching.
- `ActionFamily` classifies actions into S3/Admin/STS/KMS/Mixed for validation.
- `Statement::request_reaches_condition_eval(args, resolver)` checks action and resource gates without evaluating conditions.
- `Statement::is_allowed(args)` checks request applicability, evaluates conditions with resolver, and applies `Effect`.
- `BPStatement::request_reaches_condition_eval(args)` additionally checks principal before action/resource gates.
- `BPStatement::is_allowed(args)` evaluates bucket-policy conditions and applies effect.

## Control Flow

For identity statements, authorization builds a variable resolver from claims and request context. It rejects requests when `Action` does not match, `NotAction` matches, required resource gates fail, or `NotResource` matches. KMS statements can shortcut resource matching when the built resource is `/` or resources are empty. Admin and STS statements can skip resource matching, except table-scoped admin actions that honor resources. If the request reaches conditions, condition functions are evaluated and `Effect::is_allowed` converts the condition boolean into allow/deny semantics.

Bucket policy flow first matches the principal, then action/not-action, then resources/not-resources, then conditions. It does not have the identity-policy admin/STS/KMS resource exceptions.

`build_resource` normally builds `bucket/object`, adding a slash after bucket when object is empty. For ListBucket/ListBucketVersions/ListBucketMultipartUploads with an `s3:prefix` condition reference, it uses the bucket-only resource so the prefix is evaluated by conditions rather than by object resource matching.

## State and Persistence

Statements are in-memory data models. Evaluation constructs transient resource strings and variable resolvers only; no persistence.

## Dependencies and Integration Points

Integrates directly with action sets, resource sets, functions/conditions, effects, principals, IDs, S3 key names, and variable resolution. Called by top-level `Policy` and `BucketPolicy`. The resource construction behavior is tightly coupled to ListBucket gateway behavior and condition key handling.

## Risks and Edge Cases

- Resource handling differs by action family and admin subtype. Changes to action enum classification can affect statement validation and evaluation.
- `ActionFamily::Mixed` rejects identity statements combining S3/Admin/STS/KMS actions; `NotAction` statements bypass this classification because their allowed family is not directly knowable.
- `Effect::Deny` means `Statement::is_allowed` returns false when a deny statement matches, which top-level policy code relies on for deny-first semantics.
- `build_resource` appends `/` to bucket-only resources; resource patterns must match this convention where relevant.
- Bucket-policy statements require `Principal` and do not allow empty resource sets.

## Test Signals

Direct tests are mostly in `policy.rs` and `tests/policy_is_allowed.rs`. They exercise ListBucket prefix behavior, NotAction/NotResource validation, admin table resource scoping, STS/Admin/KMS resource exceptions, mixed-family rejection, deny behavior, and bucket-policy principal/resource interactions.
