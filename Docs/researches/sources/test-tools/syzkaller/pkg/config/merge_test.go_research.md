# sources/test-tools/syzkaller/pkg/config/merge_test.go

Purpose: Unit tests for recursive JSON merge and patch helpers.

Important APIs/types/functions: `TestMergeJSONs` and `TestPatchJSON`.

Control flow: Each table-driven test calls `config.MergeJSONs` or `config.PatchJSON`, expects no error, and compares compact JSON bytes exactly.

State and persistence behavior: In-memory only.

Dependencies/integration points: Exercises public `pkg/config` merge APIs from an external `config_test` package.

Risks: Exact byte comparisons rely on deterministic marshal ordering. Tests do not cover invalid JSON, arrays, null patches, or number type nuances.

Test signals: Confirms recursive object merging, right-side scalar replacement, empty fragment handling, and map patch insertion.
