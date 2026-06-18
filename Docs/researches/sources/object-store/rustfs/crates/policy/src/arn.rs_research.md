<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/arn.rs -->
# sources/object-store/rustfs/crates/policy/src/arn.rs

Purpose: Parses and formats RustFS IAM role ARNs. It supports a narrow ARN shape for RustFS IAM roles: `arn:rustfs:iam:<region>::role/<resource_id>`.

Important APIs/types/functions: `ARN` stores `partition`, `service`, `region`, `resource_type`, and `resource_id`. `ARN::new_iam_role_arn(resource_id, server_region)` validates and constructs a role ARN. `ARN::parse(arn_str)` validates the six colon-separated ARN components and role resource. `Display` formats the canonical ARN with an empty account ID.

Control flow: Construction and parsing both validate resource IDs with `^[A-Za-z0-9_/\\.-]+$`. Parsing checks prefix `arn`, partition `rustfs`, service `iam`, empty account-id field, resource format containing `role/`, and resource type `role`; any mismatch returns `Error::other` with a specific message.

State/persistence behavior: Stateless value object. Persistence is only the string representation emitted by `Display` or accepted by `parse`.

Dependencies/integration: Uses crate-level `Error`/`Result` and `regex::Regex`. It is intended for IAM role and STS policy integration where role ARNs are compared or stored.

Risks/test signals: The regex is compiled on every call rather than static/lazy. `split(':')` rejects ARNs with colons inside resource IDs, which is consistent with this narrow grammar. Region is accepted without validation. No tests are present in this file, so parser compatibility depends on integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/arn.rs -->
