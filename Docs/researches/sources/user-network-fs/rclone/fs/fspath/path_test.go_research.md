# sources/user-network-fs/rclone/fs/fspath/path_test.go

## Purpose
`path_test.go` is the main regression suite for rclone path parsing and joining. It captures the user-facing syntax contract for local paths, remotes, on-the-fly remotes, config parameters, quoting, Windows path handling, and root-safe joins.

## Important APIs, types, and functions
Tests target `CheckConfigName`, `MakeConfigName`, `checkRemoteName`, `Parse`, `SplitFs`, `Split`, `makeAbsolute`, and `JoinRootPath`. The `-make-corpus` test flag can emit parser corpus files for the go-fuzz harness.

## Control flow
Table-driven cases compare parsed structs and exact errors. Tests skip Windows-only or non-Windows-only expectations based on `runtime.GOOS`. `TestParse` optionally writes each input into `corpus/` when requested. Later tests verify recomposition properties such as `remoteName + remotePath == remote` and `parent + leaf == remote`.

## State and persistence behavior
Normal test runs have no persistent state. With `-make-corpus`, the test creates a `corpus` directory and writes sample inputs. Some cases compare `configmap.Simple` maps built by the parser.

## Dependencies and integration points
The suite depends on `configmap.Simple`, `filepath.FromSlash`, testify assertions, and the parser implementation. These tests protect `fs.NewFs`, CLI parsing, backend connection strings, and any code using `JoinRootPath` for canonical path construction.

## Risks and edge cases
The cases encode subtle behavior: a path with a slash before colon is local; `C:` is remote on non-Windows but a drive letter on Windows; quoted config values must terminate with comma or colon; `:backend` cannot accidentally become a local path; `JoinRootPath` preserves leading `//` for network paths.

## Test signals
Coverage is broad and high-signal. It includes invalid characters, leading/trailing spaces, Unicode remote names, boolean config params, empty config values, doubled quotes, empty path errors, Windows slash normalization, root-directory splitting, and path traversal cleanup.

Source-read signal: reviewed complete local file (646 lines). Functions/methods observed: `TestCheckConfigName`, `TestCheckRemoteName`, `TestParse`, `TestSplitFs`, `TestSplit`, `TestMakeAbsolute`, `TestJoinRootPath`.
