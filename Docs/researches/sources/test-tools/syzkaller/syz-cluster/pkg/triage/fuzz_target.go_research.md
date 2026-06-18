## sources/test-tools/syzkaller/syz-cluster/pkg/triage/fuzz_target.go

This file selects and merges fuzzing campaigns for a patch series. `SelectFuzzConfigs` matches series Cc addresses against configured `api.FuzzTriageTarget.EmailLists`, falling back to targets with no email lists only when no exact match exists. `MergeKernelFuzzConfigs` groups compatible kernel fuzz configs into fewer campaigns.

Merging groups configs by kernel config, track, and bug-title regexp. Within each group, `mergeFuzzConfigs` combines focus areas and corpus URLs, ORs `SkipCoverCheck`, and carries the common `BugTitleRe`; `unique` sorts/deduplicates strings using `maps.Keys` and `slices.Sorted`.

State is pure in-memory; no persistence. Integration points are triage workflow target generation and fuzz workflow configuration. Risks include configured `EmailLists` being compared case-sensitively on the target side while series Cc is lowercased, grouping assuming `BugTitleRe` equality but not validating other fields, and sorted unique output changing user-specified focus ordering. Unit tests cover selection fallback and merge semantics.
