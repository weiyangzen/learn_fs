# sources/test-tools/lcov/.github/dependabot.yml

Purpose: Dependabot configuration for lcov GitHub Actions dependencies. It asks Dependabot to scan workflow actions in the repository root and open weekly update pull requests.

Important APIs/types/functions: Dependabot schema `version: 2`, `updates`, `package-ecosystem: github-actions`, `directory: /`, `schedule.interval: weekly`, labels, and commit-message customization.

Control flow: GitHub Dependabot reads this file, checks action references under `.github/workflows`, and creates PRs when newer versions are available. The configured commit message prefix is `Actions` with scope included, and PRs are labeled `enhancement`.

State/persistence behavior: no runtime state in the repository beyond Dependabot-authored branches and pull requests. The schedule is weekly and not pinned to a day/time here, so GitHub chooses the exact run timing.

Dependencies/integration: integrates with GitHub's hosted Dependabot service and the workflow files that use actions such as checkout, upload-artifact, codespell, and release creation.

Risks/test signals: only GitHub Actions dependencies are covered; system packages, Perl CPAN modules, and project scripts are outside this update lane. Test signals are Dependabot successfully parsing the config and opening scoped action update PRs.
