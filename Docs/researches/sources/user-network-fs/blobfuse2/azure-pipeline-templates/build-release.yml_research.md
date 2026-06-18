# sources/user-network-fs/blobfuse2/azure-pipeline-templates/build-release.yml

## Purpose
This template installs Go, builds release binaries for Blobfuse2 and `bfusemon`, and optionally runs unit tests for release packaging contexts.

## Important APIs, Types, and Functions
Parameters include `work_dir`, `root_dir`, `unit_test`, `tags`, and `container`. It invokes `go_installer.sh`, Azure DevOps `Go@0 get`, `./build.sh <tags>`, `./build.sh health`, `blobfuse2 --version`, `bfusemon --version`, and optional `go test`.

## Control Flow
The template installs Go into the supplied root directory, downloads Go dependencies, builds Blobfuse2 with optional build tags, verifies the binary, builds and verifies the health monitor, and when `unit_test` is true writes `$HOME/azuretest.json` from pipeline storage variables before running unit tests with `--tags=unittest,<tags>`.

## State and Persistence Behavior
It creates binaries in `work_dir`, writes `$HOME/azuretest.json`, and may generate `utcover.cov`. It does not create or delete Azure containers itself.

## Dependencies and Integration Points
It integrates release build stages with shared storage account secrets and the repository build script. It is similar to `build.yml` but parameterized for release template callers.

## Risks and Edge Cases
The JSON config is assembled with shell `echo` and includes storage secrets in logs via `cat`. Unit tests depend on external Azure test accounts. Build behavior must stay aligned with `build.sh` and Microsoft Go/FIPS expectations.

## Test Signals
Signals are `blobfuse2 --version`, `bfusemon --version`, successful dependency restore, and optional unit test pass under requested build tags.
