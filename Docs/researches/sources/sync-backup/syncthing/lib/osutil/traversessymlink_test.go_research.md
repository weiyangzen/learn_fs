## sources/sync-backup/syncthing/lib/osutil/traversessymlink_test.go

Purpose: tests and benchmarks symlink traversal detection.

Important tests: `TestTraversesSymlink` builds a fake filesystem tree with directories, files, and symlinks and checks expected nil or typed errors for various paths. `TestIssue4875` covers a regression around missing paths below file/non-directory components. `BenchmarkTraversesSymlink` measures repeated safe-path checks.

Control flow and state: table-driven tests call `TraversesSymlink` and compare error types, not exact messages. Benchmark stores result in a package variable to avoid compiler elimination.

Dependencies and integration points: validates osutil safety checks used by model request handling.

Risks: fake filesystem symlink semantics may differ from all OS/filesystem combinations.

Test signals: good focused coverage for symlink traversal safety.
