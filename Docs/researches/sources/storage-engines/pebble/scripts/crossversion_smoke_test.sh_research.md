# sources/storage-engines/pebble/scripts/crossversion_smoke_test.sh

## Purpose
This script validates the cross-version metamorphic test infrastructure by proving it passes on a clean release-to-HEAD combination and fails after introducing an intentional backward-compatibility bug.

## Important APIs, Types, and Functions
It defines colored `log`, `warn`, and `error` helpers plus a `cleanup` trap. It uses a patch file `crossversion_smoke_test.patch`, the `internal/metamorphic/crossversion` package, release and head test binaries, and `go test -run TestMetaCrossVersion`.

## Control Flow
The script verifies prerequisites and a clean git workspace, finds the latest `crl-release-*` branch, checks it out to build a release metamorphic test binary, returns to the original HEAD, builds a clean HEAD binary, and runs crossversion once expecting success.

It then applies the intentional patch, builds a buggy binary, verifies the buggy binary passes single-version testing, reverts the patch, and runs crossversion with release plus buggy head for up to 10 seeds expecting at least one failure. Cleanup removes generated binaries/artifacts and reverts patch changes if still applied.

## State and Persistence Behavior
It mutates git checkout state and applies/reverts a patch. It writes test binaries and smoke artifacts under `internal/metamorphic/crossversion`, and logs under `/tmp`. Cleanup removes these generated files and may run `git checkout -- .` if the patch was applied.

## Dependencies and Integration Points
Dependencies include git, Go, release branches, the intentional patch file, metamorphic and crossversion test packages, and CI grouping markers. It integrates directly with compatibility testing infrastructure.

## Risks
The script requires a clean repository and uses `git checkout -- .` during cleanup after patch application, which would be destructive if run with uncommitted work despite the upfront cleanliness check. Release-branch discovery by lexical sort may not match semantic latest in every naming scheme. The expected failure is randomized, so it loops over seeds but could still miss a bug if the patch/test relation changes.

## Test Signals
Success means clean crossversion passed, buggy single-version passed, and buggy crossversion failed within the attempt budget. Failure messages distinguish infrastructure regression, patch mismatch, existing compatibility bugs, and inability to detect the intentional bug.
