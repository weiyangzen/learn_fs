<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/action.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/action.rs

Purpose: Defines supported IAM/S3/admin/STS/KMS action names, their serde representation, wildcard matching, and action-set behavior for policy statements.

Important APIs/types/functions: `ActionSet(Vec<Action>)` serializes as an array, deserializes from a string or array, de-duplicates entries, compares as an unordered set, and implements `is_match`. `Action` wraps `S3Action`, `AdminAction`, `StsAction`, `KmsAction`, or `None`, parses by prefix, and uses wildcard matching on string forms. Large enums enumerate supported `s3:*`, `admin:*`, `sts:*`, and `kms:*` action strings. `AdminAction::is_table_resource_scoped` identifies table-scoped admin actions; `AdminAction::is_valid` whitelists recognized admin variants.

Control flow: Deserialization accepts a single action string or sequence, parsing each through `Action::try_from`. The bare `"*"` wildcard maps to `S3Action::AllActions`. `ActionSet::is_match` returns true if any stored action wildcard-matches the requested action, with a special case allowing `s3:GetObjectVersion` to match `s3:GetObject`. `Action::try_from` returns `InvalidAction` through the outer crate error type when prefix parsing fails.

State/persistence behavior: Action sets are stored as JSON arrays of strings even for one element, supporting S3 policy compatibility. Duplicate actions are removed during deserialization, but manual `ActionSet(vec![...])` can still contain duplicates until serialized/evaluated.

Dependencies/integration: Uses serde, `strum` enum string conversions, policy wildcard utilities, crate `Error`/`Result`, and `policy::Error`. Policy statement validation and request authorization depend on this taxonomy.

Risks/test signals: The bare `"*"` mapping only becomes S3 all-actions, not all action families. `ActionSet::is_valid` currently returns `Ok(())` without checking emptiness or family mixing; those checks may live in statement/policy validators. Manual enum additions must update `AdminAction::is_valid` when applicable. Tests cover wildcard parsing, STS/KMS parsing and wildcard matching, array serialization, and many table/admin action validity cases.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/action.rs -->
