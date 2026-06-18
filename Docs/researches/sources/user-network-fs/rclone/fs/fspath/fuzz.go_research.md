# sources/user-network-fs/rclone/fs/fspath/fuzz.go

## Purpose
`fuzz.go` is a go-fuzz harness for `fspath.Parse`. It checks parser invariants across arbitrary byte strings converted to Go strings.

## Important APIs, types, and functions
The only exported fuzz entry is `Fuzz(data []byte) int`, guarded by the `gofuzz` build tag. It calls `Parse`, then verifies whether the input was preserved as a local path or split as `ConfigString + ":" + Path`.

## Control flow
Invalid parses return `0` immediately. For local paths, the harness requires an empty config string and exact path preservation. For remote paths, it requires reconstructing the original input from config string, colon, and parsed path. Any invariant violation panics for the fuzz runner to collect.

## State and persistence behavior
The harness has no persistent state. The source comment documents corpus generation and cleanup commands that create/remove local fuzz directories outside normal builds.

## Dependencies and integration points
It depends only on the package's `Parse` function and is intended to run with the legacy `github.com/dvyukov/go-fuzz` toolchain. It complements the table tests in `path_test.go`.

## Risks and edge cases
The invariant accounts for local versus remote parsing but not every Windows slash normalization nuance, so fuzz results can differ by platform if built there. It returns zero for all cases, making it a crash/invariant harness rather than a coverage-guided accept/reject classifier.

## Test signals
The presence of this harness signals that `Parse` has historically needed broad input robustness testing beyond table cases, especially around colons, quotes, commas, Unicode, and path separators.

Source-read signal: reviewed complete local file (46 lines). Functions/methods observed: `Fuzz`.
