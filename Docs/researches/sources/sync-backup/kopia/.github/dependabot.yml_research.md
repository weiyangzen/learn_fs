# sources/sync-backup/kopia/.github/dependabot.yml

Purpose: Dependabot update schedule and grouping policy.

Important APIs/types/functions: version 2 config for gomod root weekly updates, GitHub Actions monthly updates, npm `/app` monthly updates, cooldowns, PR limits, ignored `github.com/kopia/htmluibuild`, and dependency groups.

Control flow: Dependabot reads this to open grouped update PRs on schedules.

State and persistence: static repository automation config.

Dependencies and integration points: feeds auto-merge policy and dependency-review/CI workflows.

Risks: broad npm group can produce large UI PRs; cooldown delays urgent patch adoption unless manually overridden.

Test signals: Dependabot PR behavior and CI are operational signals.
