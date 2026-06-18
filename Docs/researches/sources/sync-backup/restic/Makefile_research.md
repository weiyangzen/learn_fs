# sources/sync-backup/restic/Makefile

Purpose: minimal developer Makefile for common restic build, clean, and test operations.

Control flow/state: declares phony targets `all`, `clean`, `test`, and `restic`. `all` depends on `restic`; `restic` runs `go run build.go`; `clean` removes the `restic` binary; `test` runs `go test ./cmd/... ./internal/...`.

Dependencies/integration: delegates real build logic to `build.go` and Go's test runner. It is a convenience interface for local users and CI-like manual runs.

Risks/test signals: `test` omits helper packages outside `cmd` and `internal` if any exist. `clean` removes only the Unix binary name, not `restic.exe`. Success of `go run build.go` and `go test` is the signal.
