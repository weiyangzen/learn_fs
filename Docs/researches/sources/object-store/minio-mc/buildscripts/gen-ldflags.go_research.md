<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/buildscripts/gen-ldflags.go -->
# sources/object-store/minio-mc/buildscripts/gen-ldflags.go

## Purpose
Go helper, run with `go run`, that generates linker flags embedding version, copyright year, release tag, commit hash, and short commit hash into MinIO client binaries.

## Important APIs, types, and functions
Functions are `genLDFlags`, `releaseTag`, `commitID`, `commitTime`, and `main`. It writes `-X github.com/minio/mc/cmd.*` flags for `Version`, `CopyrightYear`, `ReleaseTag`, `CommitID`, and `ShortCommitID`.

## Control flow
`main` uses an explicit version argument or formats the last commit time as RFC3339. `releaseTag` parses the version time, applies `MC_RELEASE` and optional `MC_HOTFIX`, and normalizes punctuation. Git commands retrieve commit hash/time.

## State and persistence behavior
No persistent state; output is consumed by builds and embedded into binaries.

## Dependencies and integration points
Called by Makefile, Dockerfile, and build scripts. Depends on git history, Go time parsing, and cmd package variable names.

## Risks and test signals
It panics if the version cannot be parsed as `2006-01-02T15-04-05Z` after replacement. `commitID()[:12]` assumes a full hash is available. Signal is valid ldflags output and successful binary build with version fields populated.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/buildscripts/gen-ldflags.go -->
