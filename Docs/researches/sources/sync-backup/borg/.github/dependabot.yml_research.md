# sources/sync-backup/borg/.github/dependabot.yml Research

## Purpose

`dependabot.yml` configures Dependabot updates for BorgBackup's GitHub Actions and Python requirement files. It groups update PRs to reduce churn and applies cooldowns for Python dependency updates.

## Important APIs, Types, and Functions

The file uses Dependabot config `version: 2` and two `updates` entries. The `github-actions` ecosystem scans `/` weekly and groups all actions under `actions`. The `pip` ecosystem scans `/requirements.d`, ignores `black`, runs weekly, applies semver cooldowns of 90 days for major and 30 days for minor updates, and groups all matching dependencies under `pip-dependencies`.

## Control Flow

Dependabot evaluates the schedule and opens grouped PRs according to ecosystem, directory, ignore, cooldown, and grouping rules. There is no in-repo executable flow.

## State and Persistence Behavior

Dependabot state lives in GitHub/Dependabot service data and PRs. The repository file is declarative and stores no secrets.

## Dependencies and Integration Points

It integrates with GitHub Dependabot, `.github/workflows/*`, and files under `requirements.d`. The `black` ignore aligns with the dedicated Black workflow and pinned pre-commit config, reducing formatter churn.

## Risks and Edge Cases

Grouped updates can make bisecting dependency regressions harder. Ignoring Black means formatter updates require manual maintenance. Cooldowns delay adoption of new upstream versions, trading stability for slower security or compatibility updates. Dependabot support for `cooldown` must remain compatible with GitHub's schema.

## Test Signals

Signals are Dependabot PR creation, GitHub's dependency graph/dependabot logs, and YAML/schema linting. A dry-run or service log should confirm both ecosystems are recognized.
