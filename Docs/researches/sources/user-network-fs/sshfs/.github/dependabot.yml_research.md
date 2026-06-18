# sources/user-network-fs/sshfs/.github/dependabot.yml

Purpose: Dependabot configuration for GitHub Actions updates.

Important APIs/types/functions: version 2 config, `github-actions` ecosystem at `/`, weekly schedule, 14-day cooldown, and one group matching all action updates.

Control flow: Dependabot periodically scans workflow action references and groups matching updates.

State and persistence behavior: GitHub-hosted automation state only; no runtime effect.

Dependencies and integration points: integrates with GitHub Dependabot and the repository workflows.

Risks: grouped updates reduce PR noise but can make a broken action update harder to isolate. Cooldown delays security/nonsecurity updates.

Test signals: Dependabot PR generation and successful CI after grouped action bumps.
