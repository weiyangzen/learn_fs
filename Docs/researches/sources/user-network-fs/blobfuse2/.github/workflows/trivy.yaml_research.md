# sources/user-network-fs/blobfuse2/.github/workflows/trivy.yaml

## Purpose
This workflow builds the Blobfuse2 binary and scans it with Trivy, uploading SARIF results to GitHub code scanning.

## Important APIs, Types, and Functions
It uses `actions/checkout@v6`, shell `go build -o blobfuse2`, `aquasecurity/trivy-action` pinned by commit, and `github/codeql-action/upload-sarif@v4`.

## Control Flow
The workflow runs on manual dispatch, pushes to `main`, `master`, or `blobfuse/2*`, pull requests to the same branch set, and a weekly schedule. It installs FUSE libraries, builds the binary, scans `./blobfuse2` as a filesystem target with unfixed issues ignored and all severities included, prints the SARIF file, and uploads it.

## State and Persistence Behavior
Runner state includes the built `blobfuse2` and `trivy-results-binary.sarif`. Persistent state is code scanning SARIF results in GitHub.

## Dependencies and Integration Points
It integrates binary vulnerability scanning with GitHub Security. It overlaps with CodeQL but targets dependency/binary findings rather than source queries.

## Risks and Edge Cases
The workflow scans the built binary path, not the whole repository or container image. Printing full SARIF can make logs noisy. It installs FUSE packages before build but does not use the repository's `build.sh`, so build flags may diverge.

## Test Signals
Signals are successful Go build, SARIF generation, SARIF upload, and GitHub Security tab entries matching Trivy output.
