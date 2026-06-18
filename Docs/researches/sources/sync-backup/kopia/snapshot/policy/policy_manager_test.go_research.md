# sources/sync-backup/kopia/snapshot/policy/policy_manager_test.go

Purpose: validates policy manager inheritance, conflict resolution, OS-independent path logic, subdirectory policy discovery, and path validation.

Important APIs/types/functions: tests use `SetPolicy`, `GetEffectivePolicy`, `GetDefinedPolicy`, `applicablePoliciesForSource`, `getParentPathOSIndependent`, and `validatePolicyPath`. Helpers include `clonePolicy`, `policyWithLabels`, `policyWithKeepDaily`, and `policyWithKeepMonthly`.

Control flow: inheritance tests create host and path policies, compute effective policies for multiple source infos, and compare effective policy, contributing sources, and definition metadata. Conflict test writes concurrent global policies from two repository handles and accepts either latest competing value. Applicable-policy tests create Unix and Windows-style paths, then assert the relative policy tree keys for selected roots. Path validation tests enumerate accepted and rejected trailing slash/backslash cases.

State and persistence behavior: uses real repotesting repositories and manifest writes/flushes. Conflict test demonstrates duplicate policy manifests can happen under concurrent clients and are resolved by latest ID selection.

Dependencies/integration: depends on repo test environment, `go-cmp`, `testify/require`, and snapshot source info.

Risks: one map literal has duplicate `host-c`/`C:/Users` key, so one intended case is overwritten by Go map semantics. Tests cover many path cases but not every source-label combination.

Test signals: strong coverage for the most error-prone policy-manager behavior, especially cross-platform path handling.
