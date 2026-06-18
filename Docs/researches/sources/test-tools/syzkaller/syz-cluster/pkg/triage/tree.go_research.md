## sources/test-tools/syzkaller/syz-cluster/pkg/triage/tree.go

This file contains tree-selection helpers for triage. `SelectTrees` returns ordered candidate kernel trees using subject tags, series Cc, and fallback trees. `FindTree` maps a branch string like `tree/branch` to a configured tree index and branch name. `FindTreeByName` performs direct name lookup.

`SelectTrees` lowercases series Cc addresses, treats subject tags that match a tree name as forced selections, filters out trees with non-empty email lists that do not intersect Cc, includes trees with no email lists as fallback, and stable-sorts direct subject-tag matches before other selected trees. The function preserves original configured order otherwise.

State is pure in-memory. Integration points are commit selection, base-commit hint resolution, and job/series triage. Risks include subject tags requiring exact tree-name equality and fallback trees always joining selected email-list trees. Tests cover Cc matching, fallback, direct tag preference, branch parsing, and name lookup.
