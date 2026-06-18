<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/ci.yml -->
# sources/test-tools/syzkaller/.github/workflows/ci.yml research

Purpose: main GitHub Actions CI workflow for syzkaller pushes and pull requests.

Important APIs, types, and functions: jobs include `aux`, `build`, `dashboard`, architecture matrix, race tests, old environment, and gVisor smoke testing. It uses pinned checkout/cache/upload-artifact actions, container images such as `gcr.io/syzkaller/env:latest`, `old-env`, and `syzbot`, GOPATH-style checkout paths, and `.github/workflows/run.sh` to format errors.

Control flow: pushes and PRs start a concurrency group that cancels older runs for the same PR/ref. `aux` runs `make presubmit_aux`; `build` runs `make presubmit_build` and uploads unit coverage; `dashboard` runs `make presubmit_dashboard` with a timeout and uploads dashboard coverage; `arch` fans out make targets for OS/arch builds; race jobs run race presubmits; `old` verifies older build environment support; `gvisor` builds then runs the gVisor smoke script in a privileged container.

State and persistence: CI state is limited to GitHub caches under `/syzkaller/.cache`, coverage artifacts, and job logs. The repository checkout is under `gopath/src/github.com/google/syzkaller` to satisfy tooling assumptions.

Dependencies and integration: integrates with the syzkaller Makefile presubmit targets, Google container images, GitHub cache/artifact services, and the privileged gVisor smoke environment.

Risks: container tags are mutable even when actions are SHA-pinned. `oss-fuzz` and gVisor coverage are separate, so this file's green status is not total ecosystem validation. Timeouts and high-core runner labels can cause infrastructure-dependent flakes.

Test signals: job matrix completion, uploaded `.coverage.txt` artifacts named `coverage-unittests` and `coverage-dashboard`, cache restore/update behavior, formatted annotations from `run.sh`, and cancellation of superseded PR runs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/ci.yml -->
