<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/.github/workflows/go.yml -->
# sources/object-store/minio-mc/.github/workflows/go.yml

## Purpose
Primary PR CI workflow for building and testing the MinIO client on Linux, macOS, and Windows, plus a separate 386 vet-style check.

## Important APIs, types, and functions
Uses Go 1.25.x for the build matrix, `go build`, `go test -race`, `make`, `make test-race`, `make verify`, and `functional-tests.sh`; Linux starts a local HTTPS MinIO server with bundled localhost certs. The `vetchecks` job runs Go 1.24.x and `GOOS=linux GOARCH=386 go test -short ./...`.

## Control flow
Matrix jobs set up Go, checkout, then branch by OS. Linux downloads MinIO server, installs a test CA, starts a 4-disk server, then runs full Make and functional test commands.

## State and persistence behavior
Only ephemeral CI files and local MinIO test data are created. No repository state is committed.

## Dependencies and integration points
Integrates GitHub Actions, MinIO server releases, local TLS certs, Makefile targets, Go race detector, and functional test suite.

## Risks and test signals
The Linux job depends on network download of the server binary and host certificate update permissions. Signals include race-test pass, functional test pass, and platform-specific build success.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/.github/workflows/go.yml -->
