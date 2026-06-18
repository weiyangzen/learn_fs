# sources/test-tools/syzkaller/pkg/manager/diff/patch_test.go

Purpose: Tests patch-derived focus-area construction and modified-symbol filtering.

Important tests and helpers: `TestPatchFocusAreas` creates a temporary kernel tree with one header and `.c` files, builds synthetic git diffs for a `.c` file and a header, modifies dummy symbol hashes, and asserts the exact focus-area sequence. `dummySymbolHashes` creates 100 stable symbol hashes so small deltas stay below threshold. `TestModifiedSymbols` validates both over-threshold suppression and sorted below-threshold output.

Control flow and state: The test mutates a `mgrconfig.Config` in place through `PatchFocusAreas` and checks that focus areas are appended with names `symbols`, `files`, `included`, and the final empty fallback. It also validates sorted direct and transitive file lists.

Dependencies and integration: Uses `osutil.FillDirectory` for fixture setup, `mgrconfig.FocusArea`/`CovFilterCfg` for expected values, and testify assertions. The synthetic diff format verifies integration with `vcs.ParseGitDiff` without requiring a git repository.

Risks: The test encodes exact weights and area ordering, so intended tuning changes require updates. It covers only one header include style and does not exercise the widespread-header cutoff.

Test signals: Provides high confidence that patch focus metadata reaches the manager config in the shape expected by coverage filtering.
