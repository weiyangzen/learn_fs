# sources/sync-backup/restic/build.go

Purpose: `go run build.go` build helper for restic. It enforces a minimum Go version, sets default build tags, embeds version information, supports cross-compilation flags, and optionally runs tests.

Important APIs/types/functions: `Config` describes binary name, namespace, main package, default tags, tests, and minimum Go version. `GoVersion`, `ParseGoVersion`, and `AtLeast` implement version checks. `build` and `test` wrap `go build`/`go test` with controlled env. `getVersionFromFile`, `getVersionFromGit`, `getVersion`, and `Constants.LDFlags` compute `main.version` ldflags.

Control flow: `main` rejects old Go versions, parses flags manually, builds env defaults, computes output path, strips symbols unless `debug` or `profile` tags are present, invokes `go build -trimpath` with default tags `selfupdate,disable_grpc_modules`, then optionally runs configured tests.

State/persistence: writes the binary to `restic`, `restic.exe`, or `--output`. It does not modify source state. It reads `VERSION` and Git metadata when available.

Dependencies/integration: Go toolchain, Git, runtime environment variables, and CI `Makefile`/workflow build steps.

Risks/test signals: manual flag parsing has limited bounds checks for options requiring values. Empty/unparseable Go versions are treated as satisfying all versions. CI's `Build with build.go` and cross-platform matrix exercise this file.
