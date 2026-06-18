# sources/sync-backup/kopia/snapshot/policy/policy_tree_test.go

Purpose: unit tests for policy tree child lookup and construction from dot-rooted policy maps.

Important APIs/types/functions: package-level sample policies `defPolicy`, `policyA`, `policyB`, `policyC`, `TestTreeChild`, `TestBuildTree`, `verifyTreePolicy`, and `dumpTree`.

Control flow: `TestTreeChild` manually constructs a tree and checks nil tree fallback, direct children, missing siblings, and inherited descendants. `TestBuildTree` uses `BuildTree` with policies at `.`, `./foo`, and `./bar/baz/bleh`, then queries paths containing empty and `"."` segments.

State and persistence: all state is in-memory `Tree` and `Policy` values. The test intentionally compares pointers/deep equality rather than stored repository policies.

Dependencies and integration points: validates behavior required by policy-aware filesystem traversal where `Tree.Child(name)` is called for every path element.

Risks and test signals: `dumpTree` prints to stdout and is diagnostic noise, but not behavioral. Signals are exact effective policy and `IsInherited` values for each path case.
