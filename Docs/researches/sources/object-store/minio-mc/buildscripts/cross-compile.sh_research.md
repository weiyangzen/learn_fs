<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/buildscripts/cross-compile.sh -->
# sources/object-store/minio-mc/buildscripts/cross-compile.sh

## Purpose
Noninteractive cross-compilation smoke test for MinIO client across supported OS/ARCH targets.

## Important APIs, types, and functions
Functions `_init`, `_build`, and `main`. It sets `CGO_ENABLED=0`, enumerates target pairs, sets `GOOS`, `GOARCH`, `GO111MODULE`, and runs `go build -tags kqueue -o /dev/null`.

## Control flow
The script exits on first error. `main` loops all target pairs and invokes `_build`, which prints the target and package import path before compiling.

## State and persistence behavior
No persistent build artifacts are kept because output goes to `/dev/null`.

## Dependencies and integration points
Used by `make crosscompile` and the `go-cross` workflow. Depends on Go cross-compilation support for listed targets.

## Risks and test signals
The target list includes less common architectures; dependency build tags must remain portable. Signal is completion of every target without compile failure.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/buildscripts/cross-compile.sh -->
