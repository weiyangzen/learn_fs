<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/.github/dependabot.yml -->
# sources/test-tools/strace/.github/dependabot.yml

Purpose: Dependabot configuration for keeping GitHub Actions dependencies current.

Important declarations: version 2 config with one update block for `package-ecosystem: github-actions`, `directory: /`, monthly schedule, a seven-day cooldown, and at most two open PRs.

Control flow: no runtime logic; GitHub Dependabot reads it on schedule.

State and persistence: external service state consists of generated dependency update pull requests.

Dependencies and integration: targets pinned actions in `.github/workflows/*.yml`, including checkout, Codecov, differential-shellcheck, and upload-artifact.

Risks: only GitHub Actions are covered; container images, GitLab CI base images, Packit, and shell dependencies are not. The cooldown and PR cap intentionally slow update velocity. Test signals: GitHub dependency graph/Dependabot logs should show monthly action update checks from repository root.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/.github/dependabot.yml -->
