<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/buildscripts/build.sh -->
# sources/object-store/minio-mc/buildscripts/build.sh

## Purpose
Interactive release-build script for producing versioned MinIO client binaries and checksum files for selected OS/ARCH targets.

## Important APIs, types, and functions
Functions are `_init`, `go_build`, and `main`. It derives LDFLAGS from `gen-ldflags.go`, validates `MC_RELEASE`, defines supported targets, uses `go build`, copies downloadable binaries, and writes SHA1/SHA256 checksum files.

## Control flow
Initialization extracts release tag/string and tool paths. `main` prompts for all or one supported target, validates input, and calls `go_build` for each. `go_build` computes names, compiles with `CGO_ENABLED=0`, copies platform-specific binary names, and generates checksum files.

## State and persistence behavior
Creates release directories, binaries, copied aliases, and checksum files. It may overwrite release output paths.

## Dependencies and integration points
Depends on bash, Go, git-derived ldflags, `shasum`, `sed`, and environment variable `MC_RELEASE`.

## Risks and test signals
Interactive prompt makes it unsuitable for noninteractive CI unless input is provided. Supported target list is narrower than cross-compile CI. Signal is all selected binaries and checksum files created.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/buildscripts/build.sh -->
