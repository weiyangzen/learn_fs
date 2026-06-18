<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/upload-coverage.yml -->
# sources/test-tools/syzkaller/.github/workflows/upload-coverage.yml research

Purpose: privileged coverage upload workflow that runs after successful `ci` workflow runs and publishes unit/dashboard coverage to Codecov.

Important APIs, types, and functions: triggered by `workflow_run` completion for workflow `ci`, with read-only contents/actions permissions. It uses SHA-pinned checkout, download-artifact, and Codecov actions, checks out untrusted head code without persisted credentials, checks out the trusted base `.github/codecov.yml`, fetches a PR number with `gh pr list`, and uploads two named coverage artifacts with separate Codecov flags.

Control flow: the job runs only when the upstream CI conclusion is `success`. It checks out the head repository/commit, checks out a sparse trusted base config into `base-repo`, downloads artifacts for the triggering run id, resolves PR number from the head SHA or workflow payload, then uploads `coverage-unittests` and `coverage-dashboard` with override commit/PR values.

State and persistence: consumes GitHub artifacts and secrets (`CODECOV_TOKEN`, `GITHUB_TOKEN`) in a privileged base-repository context. It persists coverage only to Codecov.

Dependencies and integration: integrates with artifact names emitted by `ci.yml`, Codecov configuration, GitHub CLI, repository secrets, and the `workflow_run` trust boundary.

Risks: the comments document the key security issue: this privileged workflow checks out untrusted fork code. `persist-credentials: false`, trusted sparse config checkout, pinned actions, and explicit artifact run id reduce that risk, but any future step that executes untrusted code here would be dangerous.

Test signals: workflow should skip failed CI runs, download the expected two artifacts, resolve PR numbers for fork PRs, and show Codecov uploads against the head SHA rather than the default branch workflow commit.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/upload-coverage.yml -->
