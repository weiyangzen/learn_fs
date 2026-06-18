# sources/user-network-fs/rclone/lib/israce/israce.go

Source read signal: reviewed complete local file (9 lines, sha256 981d6f5c52b8079d).

Purpose: Reports race-detector-enabled builds.

Important APIs/types/functions: Under the `race` build tag, exports `const Enabled = true`.

Control flow: No runtime flow; build tags select the file.

State and persistence behavior: No state.

Dependencies and integration points: Package can be used by tests or runtime code that adjust behavior under `go test -race`.

Risks and test signals: Correctness depends entirely on Go build tag selection.
