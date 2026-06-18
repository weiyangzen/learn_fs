# sources/test-tools/kdevops/.github/workflows/kdevops.yml

Purpose: main kdevops CI workflow for scheduled, push, pull request, and manual runs on self-hosted runners. It configures kdevops, brings up guests, installs Linux/tests, runs tests, archives results, and cleans up.

Important APIs/types/functions: triggers include daily cron, push, pull request, and `workflow_dispatch` inputs for workflow, kernel tree/ref, test mode, guest OS, and custom tests. Jobs are `generate_kernel_ref`, `check_ref`, and matrix job `ci-matrix`. The workflow composes local actions `configure`, `bringup`, `linux`, `build-test`, `test`, `archive`, and `cleanup`.

Control flow: scheduled runs generate a kernel ref from `scripts/korg-releases.py`, using mainline on Mondays and linux-next otherwise. Manual runs validate `kernel_ref` against `/mirror/<tree>.git`. The matrix selects `blktests` for schedule, one requested workflow for manual dispatch, or a small default push/PR matrix. Each matrix lane fresh-cleans the workspace, clones the repository with optional local mirror reference, checks out PR head or event ref, reports commit metadata, then runs the local composite actions. Test timeout is 24 hours for linux-ci/schedule and 2 hours for kdevops-ci. Cleanup always runs.

State/persistence behavior: deliberately deletes workspace contents at job start, creates guests and workflow state through kdevops, writes CI metadata files, uploads archive artifacts, and destroys guests in cleanup.

Dependencies/integration: depends on self-hosted runner labels `kdevops-ci` and `linux-ci`, local mirrors under `/mirror`, secrets `SSH_PRIVATE_KEY`, local action files, kdevops defconfigs, and all CI make targets.

Risks/test signals: the manual ref check assigns `contains_tag` using `git branch --contains` rather than tag inspection, so tag validation may be weaker than intended. `rm -rfv ./* ./.*` is intentionally aggressive inside the runner workspace. Test signal is a full successful matrix lane with archive artifact and cleanup, plus skipped/success needs logic allowing non-applicable preparatory jobs.
