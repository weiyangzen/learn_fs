# sources/sync-backup/syncthing/.github/ISSUE_TEMPLATE/02-bug.yml

Purpose: GitHub issue form for bug reports. It labels new issues as `bug` and `needs-triage`, sets type `Bug`, warns users away from security reports and support questions, and gathers reproduction details, Syncthing version, platform, optional browser version, and logs.

Important APIs/types/functions: body elements include a markdown warning, required textareas/inputs `what-happened`, `version`, and `platform`, optional `browser`, and shell-rendered `logs`.

Control flow: GitHub renders warnings first, then validates required fields before issue creation. Logs are formatted as shell output automatically.

State and persistence behavior: no local state. Submitted form data becomes persistent GitHub issue content used for debugging and triage.

Dependencies/integration: integrates with GitHub Issues, the forum/support split, security policy, and release-note label categories.

Risks/test signals: missing API-key redaction or private paths in user logs remain a user-submission risk. Maintainer signal is consistently labeled bug reports with version and platform fields present.
