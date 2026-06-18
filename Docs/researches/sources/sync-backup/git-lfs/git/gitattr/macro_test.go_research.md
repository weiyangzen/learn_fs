# sources/sync-backup/git-lfs/git/gitattr/macro_test.go

Purpose: tests macro expansion and macro state behavior.

Important APIs/types/functions: `ParseLines`, `NewMacroProcessor`, `ProcessLines`, and `ProcessMacros`.

Control flow: test cases parse macro definitions and pattern lines, run the processor with macros enabled or disabled, and assert expanded ordered attributes. Separate cases validate `!macro` expansion into unspecified attributes, built-in `binary`, state reuse across calls, and overriding an existing macro definition.

State/persistence behavior: intentionally verifies persistent macro state in one processor instance and override behavior through `ProcessMacros`.

Dependencies/integration: uses `testify/assert`. Supports `Tree.Applied` and `files.go` assumptions that macro expansion order is stable.

Risks/test signals: strong for macro semantics, but not for concurrency or sharing a processor across unrelated repositories.
