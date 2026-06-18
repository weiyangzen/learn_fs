# sources/sync-backup/kopia/snapshot/policy/policy.go

Purpose: defines the top-level snapshot policy schema, definition-source schema, target wrapper, validation entrypoint, and policy path validation.

Important APIs/types/functions: `ErrPolicyNotFound`, `TargetWithPolicy`, `Policy`, `Definition`, `Policy.String`, `Policy.ID`, `Policy.Target`, `ValidatePolicy`, and `validatePolicyPath`.

Control flow: `String` pretty-prints policy JSON. `ID` and `Target` read labels assigned by policy manager. `ValidatePolicy` delegates to scheduling and upload validation. `validatePolicyPath` rejects trailing slash/backslash except root paths.

State and persistence behavior: `Policy` fields persist as manifest JSON; `Labels` are not persisted in the payload but attached from manifest metadata. `Definition` is computed to explain where effective values came from.

Dependencies/integration: composes retention, files, error handling, scheduling, compression, splitter, actions, OS snapshot, logging, and upload policy subtypes. Uses path helpers from `policy_manager.go`.

Risks: `Policy.ID` assumes labels are populated and can return empty string otherwise. `validatePolicyPath` indexes the last byte and assumes non-empty path; callers only invoke it when path is non-empty.

Test signals: policy manager tests cover path validation and effective policy labels; scheduling/upload validation tests live elsewhere.
