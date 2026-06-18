# sources/user-network-fs/rclone/.github/ISSUE_TEMPLATE/config.yml

Purpose: Configures GitHub issue creation behavior for rclone by disabling blank issues and directing support requests to the forum.

Important APIs/types/functions: `blank_issues_enabled: false` and one `contact_links` entry named `Rclone Forum Community Support`.

Control flow: GitHub reads this when rendering issue templates. Users cannot open blank issues through the normal UI and see the forum link.

State and persistence: Repository configuration only.

Dependencies and integration points: Integrates with GitHub Issues UI and the rclone forum.

Risks: Users with bug reports that do not match templates may be redirected away from GitHub. The forum URL is an external dependency.

Test signals: No automated tests; effect is visible in GitHub UI.
