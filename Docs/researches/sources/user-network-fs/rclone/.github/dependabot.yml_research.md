# sources/user-network-fs/rclone/.github/dependabot.yml

Purpose: Configures Dependabot updates for GitHub Actions used by rclone.

Important APIs/types/functions: Version 2 config with `package-ecosystem: github-actions`, root directory `/`, and daily schedule.

Control flow: Dependabot periodically scans workflow action references and proposes update PRs.

State and persistence: Repository automation policy only.

Dependencies and integration points: Integrates with GitHub Dependabot and workflow files under `.github/workflows`.

Risks: Daily action-update PRs can introduce CI changes or noise. It does not cover Go modules or Docker base images.

Test signals: Dependabot PRs and subsequent CI runs are the validation signal.
