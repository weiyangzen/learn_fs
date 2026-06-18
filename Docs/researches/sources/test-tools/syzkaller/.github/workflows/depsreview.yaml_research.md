<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/depsreview.yaml -->
# sources/test-tools/syzkaller/.github/workflows/depsreview.yaml research

Purpose: pull-request dependency review workflow.

Important APIs, types, and functions: grants read-only contents permission, checks out the repository with a SHA-pinned `actions/checkout`, then runs a SHA-pinned `actions/dependency-review-action`.

Control flow: every pull request triggers a single `dependency-review` job on `ubuntu-latest`. The action compares dependency changes and reports policy/security findings.

State and persistence: no repository state is modified. Results are stored as GitHub checks/logs.

Dependencies and integration: depends on GitHub's dependency graph and the dependency-review action.

Risks: the action and checkout are pinned, but the runner image is not. Findings depend on supported ecosystems and GitHub advisory data.

Test signals: PR checks should include Dependency Review, fail or warn according to dependency-review defaults, and show only read permissions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/depsreview.yaml -->
