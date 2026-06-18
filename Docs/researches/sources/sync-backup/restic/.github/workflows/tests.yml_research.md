# sources/sync-backup/restic/.github/workflows/tests.yml

Purpose: main restic CI workflow for tests, cross-compilation, linting, Docker build validation, and aggregate status analysis.

Control flow/state: triggers on pushes to `master`, pull requests, and merge queue. The `test` matrix runs Windows, macOS, Linux latest, Linux race, and Linux minimum-Go lanes. It installs Go, rest-server, minio, rclone, and Windows tar dependencies, builds via `go run build.go`, runs a minimal init/backup smoke test, runs `go test -cover`, optionally tests cloud backends using secrets, and optionally checks changelog files. `cross_compile` runs release binary builds in three platform subsets. `lint` runs golangci-lint for PRs and verifies `go mod tidy`. `analyze` gates all required jobs with `re-actors/alls-green`. A separate `docker` job validates `docker/Dockerfile`.

Dependencies/integration: GitHub Actions, Go 1.25/1.26, external tool downloads, cloud secrets, backend test environment variables, Buildx/QEMU, and restic helper build scripts.

Risks/test signals: uses some moving upstream downloads and `@master/@latest` Go installs. Cloud tests are skipped for untrusted PRs/Dependabot. This workflow is the strongest automated signal for files in this subset.
