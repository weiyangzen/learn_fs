# Research: sources/sync-backup/syncthing/meta/gofmt_test.go

## sources/sync-backup/syncthing/meta/gofmt_test.go

Purpose: enforces canonical Go formatting and simplification.

Important APIs/functions: `TestCheckGoFmt` walks `gofmtCheckDirs` and runs `gofmt -s -d` on each non-generated Go file.

Control flow: for every eligible file, it invokes `exec.Command("gofmt", "-s", "-d", path)`. Command errors fail the walk, and non-empty diff output is reported as a formatting failure.

State and persistence: read-only check; it does not rewrite files.

Dependencies and integration: depends on a `gofmt` binary in PATH and the Go toolchain. It integrates with CI and local developer checks. Risks are environment-related failures when `gofmt` is missing and skipped `.pb.go` generated files. Test signal is the exact diff emitted by `gofmt`.
