# sources/test-tools/lcov/.github/workflows/codespell.yml

Purpose: GitHub Actions workflow that enforces spelling cleanliness with codespell on pull requests, pushes, weekly scheduled runs, and manual dispatch.

Important APIs/types/functions: workflow triggers, restricted `permissions: contents: read`, `actions/checkout@v6`, and `codespell-project/actions-codespell@v2` with `ignore_words_list`.

Control flow: a single `codespell` job runs on `ubuntu-24.04`, checks out the repository, and invokes the codespell action. Ignored tokens are documented inline as man-page markup, abbreviations, or variable names that should not fail the run.

State/persistence behavior: no repository state is modified. The only persisted outputs are GitHub Actions logs and check results associated with the commit or PR.

Dependencies/integration: integrates with GitHub Actions and the external codespell action. It complements the local `make checkstyle` Perl formatting lane by catching spelling issues across the tree.

Risks/test signals: ignore words must remain lowercase and comma-separated, as noted in the file. New project-specific terms may need additions or the job can produce false positives. The primary signal is the job status on PRs and scheduled weekly runs.
