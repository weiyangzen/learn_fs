# sources/sync-backup/restic/helpers/prepare-release/main.go

## Purpose

This Go helper orchestrates restic's release preparation. It validates release preconditions, updates generated docs/completions and version files, creates signed tags and source tarballs, builds release binaries in Docker, writes checksums/signatures, prepares Docker publish commands, and prints final push/cleanup instructions.

## Important APIs, Types, and Functions

- `opts` captures release version and ignore flags for branch, uncommitted changes, changelog checks, Docker builder Go version, plus output directory.
- `versionRegex` requires semantic `x.y.z` versions.
- Utility functions `die`, `msg`, `run`, `replace`, `rm`, `rmdir`, `mkdir`, `getwd`, `readdir`, and `tempdir` handle process execution and filesystem work.
- Git/release prechecks: `uncommittedChanges`, `getBranchName`, `preCheckBranchMaster`, `preCheckUncommittedChanges`, `preCheckVersionExists`.
- Changelog functions: `preCheckChangelogCurrent`, `preCheckChangelogRelease`, `createChangelogRelease`, and `preCheckChangelogVersion`.
- `preCheckDockerBuilderGoVersion` compares local `go version` with the `restic/builder` container's Go version.
- `generateFiles` builds a temporary restic binary and regenerates man pages plus bash, fish, PowerShell, and zsh completions under `doc/`, committing changes when present.
- `updateVersion` writes `VERSION`, updates `internal/global/global.go`, and commits if changed.
- `updateVersionDev` resets files to the next dev version and commits.
- `addTag` creates a signed annotated `v<version>` tag.
- `exportTar` creates a gzip-normalized git archive.
- `extractTar` unpacks the source archive into a build source directory.
- `runBuild` runs `helpers/build-release-binaries/main.go` inside `restic/builder`.
- `sha256sums` writes checksums for all files in the output directory.
- `signFiles` creates detached armored GPG signatures.
- `updateDocker` creates a Docker buildx builder, validates release Dockerfile build, and returns commands to push `latest` and version tags.

## Control Flow

`main` requires a version argument, validates its format, runs branch/uncommitted/tag/builder/changelog prechecks, creates a changelog release directory if needed, and ensures `CHANGELOG.md` contains the version. It creates output/source temp dirs as needed, regenerates generated docs/completions, commits release version changes, creates a signed tag, commits the post-release development version, exports a source tarball from the tag, extracts it, builds release binaries in Docker, writes `SHA256SUMS`, signs checksums and tarball, builds Docker images without pushing, and prints the exact `git push --tags` and `docker buildx` publish commands to run.

## State and Persistence Behavior

This helper intentionally mutates the working tree and git repository: it can move changelog files, regenerate `doc/`, write `VERSION`, modify `internal/global/global.go`, create commits, and create a signed tag. It writes release artifacts to `opts.OutputDir`, temporary source/build directories under the current working directory, `SHA256SUMS`, `.asc` signatures, and returns Docker builder cleanup commands. It also pulls and builds Docker images.

## Dependencies and Integration Points

It depends on Git, GPG, Docker/buildx, the `restic/builder` image, local Go, `calens`, tar/gzip, sha256sum, pflag, generated documentation commands, and `helpers/build-release-binaries`. It integrates with restic release conventions: changelog directories, `CHANGELOG.md`, `VERSION`, `internal/global/global.go`, generated `doc` assets, signed tags, GitHub release artifacts, and Docker image publishing.

## Risks and Edge Cases

- This is a high-impact mutating release script; running it in the wrong branch or dirty tree is guarded unless ignore flags are used.
- `preCheckChangelogCurrent` may create a commit automatically after regenerating `CHANGELOG.md`.
- `createChangelogRelease` moves all unreleased changelog files except `.gitignore`.
- GPG signing and Docker buildx state must be configured correctly.
- `updateDocker` creates a randomly named builder and prints cleanup, but if the process fails before the printed cleanup command, builders may remain.
- Release reproducibility depends on builder image Go version matching local Go and on deterministic tar/compression settings.

## Test Signals

Dry-run style testing is limited because the script commits/tags by design. Validation signals include running with ignore flags in a disposable clone, successful generated doc diffs, signed tag creation, successful builder container comparison, successful binary builds, valid `SHA256SUMS`, and subsequent `verify-release-binaries.sh` reproduction.
