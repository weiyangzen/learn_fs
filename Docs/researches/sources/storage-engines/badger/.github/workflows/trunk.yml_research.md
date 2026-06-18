# sources/storage-engines/badger/.github/workflows/trunk.yml

Purpose: delegates pull-request code-quality checks to a shared Dgraph Trunk workflow.

Important flow: on PRs to `main`, with read access to contents and write access to actions/checks, the single job uses `dgraph-io/.github/.github/workflows/trunk.yml@main`.

State and persistence: results are GitHub checks created by the reusable workflow. Dependencies are the shared workflow repository, Trunk configuration in `.trunk/trunk.yaml`, and repository permissions. Risks: behavior can change when the shared workflow's `main` branch changes, and write permissions to actions/checks are broader than pure lint jobs need. Test signals include workflow invocation success, Trunk check output, and actionlint validation.
