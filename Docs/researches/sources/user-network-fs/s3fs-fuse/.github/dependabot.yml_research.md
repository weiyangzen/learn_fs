<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/.github/dependabot.yml -->
# sources/user-network-fs/s3fs-fuse/.github/dependabot.yml

Purpose: Configures Dependabot updates for GitHub Actions used by the s3fs-fuse repository.

Important fields: Uses Dependabot config version 2 with one update entry for `package-ecosystem: "github-actions"`, `directory: "/"`, and a monthly schedule.

Control flow and integration: GitHub reads this file outside the build. It affects workflow dependency freshness, especially actions such as `actions/checkout`.

State and persistence: No runtime state. Dependabot opens pull requests according to the schedule.

Dependencies and risks: Only GitHub Actions dependencies are covered; container image tags, OS packages, curl direct binary versions, and autotools/library versions are not managed here. Monthly cadence reduces churn but may delay security fixes.

Test signals: GitHub Dependabot UI should show the config as valid. Changes are validated by observing generated update PRs and CI behavior on those PRs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/.github/dependabot.yml -->
