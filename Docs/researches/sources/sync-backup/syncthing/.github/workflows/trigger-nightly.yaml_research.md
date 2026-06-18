# sources/sync-backup/syncthing/.github/workflows/trigger-nightly.yaml

Purpose: scheduled/manual nightly release trigger.

Important APIs/types/functions: workflow runs at 01:00 UTC daily or manually, grants contents write, checks out full history with `ACTIONS_GITHUB_TOKEN`, and pushes `main` to `release-nightly`.

Control flow: the push updates the `release-nightly` branch, which in turn activates release-gated paths in the main build workflow.

State and persistence behavior: mutates the remote `release-nightly` branch and indirectly causes nightly artifacts to be produced.

Dependencies/integration: depends on the main branch, write-capable token, and `build-syncthing.yaml` jobs keyed to `release-nightly`.

Risks/test signals: force-like branch update semantics are not used, but pushing main to nightly can fail on branch protection or divergent refs. Signal is a successful branch update followed by nightly build/publish jobs.
