# sources/sync-backup/kopia/snapshot/policy/policy_merge_test.go

Purpose: reflective regression coverage for Kopia snapshot policy definition and inheritance merge behavior. It ensures every `policy.Policy` field has a matching `policy.Definition` provenance field unless explicitly omitted, and that `MergePolicies` chooses child, parent, and default values correctly.

Important APIs/types/functions: `TestPolicyDefinition`, `ensureTypesMatch`, `TestPolicyMerge`, `testPolicyMergeSingleField`, `policyWithField`, `disableParentMerging`, plus focused tests for `CompressionPolicy.OnlyCompress` and `SchedulingPolicy.TimesOfDay`. The tests use `reflect.TypeFor`, `snapshot.SourceInfo`, `policy.DefaultPolicy`, and `policy.MergePolicies`.

Control flow: generic reflection cases synthesize policies with zero, parent, and child values, then compare stringified merged policies. Special tests leave parent merging enabled to validate append, sort, dedupe, and `NoParent` cutoffs.

State and persistence: no repository state is written; the observable state is merged in-memory policy plus definition metadata.

Dependencies and integration points: covers all policy substructs, optional scalar wrappers, compression names, action commands, OS snapshot modes, and labels used to derive targets.

Risks and test signals: reflection only handles known field types, so adding a policy field requires updating this test. Signals are exact `String()` equality and definition JSON tag parity.
