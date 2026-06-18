# sources/user-network-fs/blobfuse2/blobfuse2-1es_ci.yaml

## Purpose
This Azure DevOps 1ES CI pipeline runs official compliance-backed CI for PRs, including mirrored fork PR branches, with build, unit tests, lint, formatting, notices, copyright, cleanup, and component governance.

## Important APIs, Types, and Functions
It triggers on `pr-mirror/*` branches and PRs to `main` excluding documentation-only paths. It extends `v1/1ES.Official.PipelineTemplate.yml@1esPipelines`, uses Windows source analysis pool settings, and composes `azure-pipeline-templates/build.yml` and `cleanup.yml`. It runs `golangci-lint v2.11.0`, `gofmt`, `notices_fix.sh`, grep copyright checks, and `ComponentGovernanceComponentDetection@0`.

## Control Flow
The CI stage runs a distro/architecture matrix for Ubuntu 20, Ubuntu 22, and Ubuntu 22 ARM64 on 1ES pools. Each job builds and runs unit tests, executes lint with build tags, checks current-year Microsoft copyright headers, checks Go formatting, regenerates NOTICE and verifies diff size, deletes containers, then runs component governance.

## State and Persistence Behavior
It creates temporary Azure containers through `build.yml`, writes coverage/log files locally, mutates NOTICE in the workspace for diff checking, and relies on `cleanup.yml` to delete containers. Compliance results persist in Azure DevOps/1ES systems.

## Dependencies and Integration Points
It connects GitHub PR mirroring (`pr-mirror.yml`) to Azure DevOps. It depends on variable group `NightlyBlobFuse`, 1ES templates, custom agent pools, build templates, and the repository lint config.

## Risks and Edge Cases
The mirror-branch trigger must be paired with trusted YAML loading to avoid fork-authored pipeline changes. Lint logic expects one line of output for no issues, which is fragile. `cleanup.yml` with `unmount: false` deletes containers but does not clean mount state.

## Test Signals
Signals include passing matrix jobs, clean lint/format/notice/copyright checks, deleted temporary containers, and component governance registration without high alerts.
