<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/.github/workflows/go-cross.yml -->
# sources/object-store/minio-mc/.github/workflows/go-cross.yml

## Purpose
GitHub Actions pull-request workflow that verifies MinIO client cross-compilation on Ubuntu with Go 1.25.x.

## Important APIs, types, and functions
Workflow `Crosscompile` runs on PRs to `master`, has concurrency cancellation per branch, read-only contents permission, checks out code, sets up Go, enables IPv6 sysctls, and runs `make crosscompile` with `CGO_ENABLED=0` and modules on.

## Control flow
For each matrix entry, checkout/setup precede the Ubuntu-only build step. The Make target delegates to `buildscripts/cross-compile.sh`.

## State and persistence behavior
No repo state is written except ephemeral CI workspace build cache/artifacts.

## Dependencies and integration points
Depends on GitHub Actions, Go toolchain, Makefile, and cross-compile script.

## Risks and test signals
The workflow only runs Ubuntu despite a matrix dimension. Build failures indicate target OS/ARCH compile regressions; IPv6 sysctl failures would break the job environment.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/.github/workflows/go-cross.yml -->
