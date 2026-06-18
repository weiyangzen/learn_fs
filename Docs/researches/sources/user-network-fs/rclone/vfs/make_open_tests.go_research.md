<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/make_open_tests.go -->
# sources/user-network-fs/rclone/vfs/make_open_tests.go

## Purpose
Generates `open_test.go`, a table of expected VFS open semantics for combinations of read/write mode, append, create, exclusive, sync, and truncation flags. It records Unix-like behavior with an intentional rclone adjustment for `O_RDONLY|O_TRUNC`.

## Important APIs, Types, and Functions
Key functions are `whichError`, `test`, and `main`; `accessModeMask` mirrors the VFS flag mask. The generated table uses `openTest` records with expected open/read/write errors and final contents.

## Control Flow
For each flag combination, `test` opens a nonexistent file, optionally reads/writes/closes it, creates a baseline file containing `hello`, opens it with the same flags, reads/writes/closes, reads final contents, removes the file, normalizes expected errors, and prints a Go struct literal. `main` enumerates all combinations and emits a complete Go source file.

## State and Persistence Behavior
The generator mutates a temporary local OS file and uses the observed local filesystem behavior as the oracle. Generated output persists only when run through `go generate` from `vfs.go`, which pipes the result through `gofmt` into `open_test.go`.

## Dependencies and Integration Points
Depends on `github.com/rclone/rclone/lib/file` wrappers and standard `os` behavior. It integrates with `read_write_test.go`, whose open matrix tests consume `openTests`.

## Risks and Edge Cases
`O_SYNC` is captured in the matrix but VFS largely ignores it. The generator has a hardcoded override for `O_RDONLY|O_TRUNC`, because Linux truncates but VFS chooses `EINVAL`. Error recognition is string-based for several OS errors, so new platform messages could break generation. It is build-tagged `none`, so it is not compiled in normal builds.

## Test Signals
The file is itself a test-data generator. Its signal appears through `open_test.go` and `TestRWFileHandleOpenTests`, not through direct execution in ordinary test runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/make_open_tests.go -->
