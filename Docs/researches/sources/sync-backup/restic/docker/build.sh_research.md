# sources/sync-backup/restic/docker/build.sh

## Purpose

This shell script builds the local Docker image `restic/restic:latest` using the repository's Dockerfile and root as build context.

## Important APIs, Types, and Functions

- Resolves `root` from the script path using `readlink -f "$0"` and two `dirname` calls.
- Uses `set -e` to stop on failures.
- Exports `DOCKER_BUILDKIT=${DOCKER_BUILDKIT-1}` to enable BuildKit by default unless already set.
- Runs `docker build --rm --pull --file "$root"/docker/Dockerfile --tag restic/restic:latest "$root" "$@"`.

## Control Flow

The script determines the repository root independent of caller working directory, enables BuildKit by default, prints a build message, and delegates to `docker build`. Additional user-provided arguments are appended after the build context.

## State and Persistence Behavior

It creates or updates the local Docker image tag `restic/restic:latest` and may update local Docker build cache/layers. It does not write repository files.

## Dependencies and Integration Points

It depends on POSIX `sh`, `readlink`, `dirname`, and Docker. It integrates with `docker/Dockerfile` and is likely used by developers or packaging automation for local image builds.

## Risks and Edge Cases

- `readlink -f` is not portable to all macOS environments without GNU coreutils.
- Appending `"$@"` after the context is unusual for some Docker CLI options; many options must appear before the context to be accepted.
- `--pull` can change base image versions and reduce reproducibility.

## Test Signals

Running `docker/build.sh` successfully and then `docker run --rm restic/restic:latest version` provides a basic validation signal.
