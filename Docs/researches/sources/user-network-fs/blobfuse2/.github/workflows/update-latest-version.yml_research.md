# sources/user-network-fs/blobfuse2/.github/workflows/update-latest-version.yml

## Purpose
This workflow updates the `benchmarks` branch release sentinel used by Blobfuse2 version checks whenever a non-preview `blobfuse2-*` release tag is pushed.

## Important APIs, Types, and Functions
It uses `actions/checkout@v6`, shell tag parsing via `${GITHUB_REF_NAME#blobfuse2-}`, `rm -f *`, `touch`, git add/commit/push, and a job-level `if` excluding tag names containing `preview`.

## Control Flow
On `blobfuse2-*` tag push, non-preview tags check out the `benchmarks` branch, derive the version, enter `release/latest/`, remove all existing sentinel files, create an empty file named after the new version, and commit/push only if changes are staged.

## State and Persistence Behavior
Persistent state is `release/latest/<version>` on the `benchmarks` branch. The workflow intentionally represents the latest version as an empty filename.

## Dependencies and Integration Points
It integrates release tags with Blobfuse2's runtime latest-version check against raw GitHub content on the `benchmarks` branch.

## Risks and Edge Cases
`rm -f *` is destructive within `release/latest/` and assumes that directory exists and contains only sentinel files. Preview exclusion is a substring check. Concurrent tag pushes can race on the branch.

## Test Signals
Signals are a new sentinel file in `benchmarks:release/latest/`, no commit when already current, and runtime version check resolving the expected latest release.
