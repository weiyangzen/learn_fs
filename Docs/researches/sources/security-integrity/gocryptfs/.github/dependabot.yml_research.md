# sources/security-integrity/gocryptfs/.github/dependabot.yml

Purpose: This Dependabot configuration keeps gocryptfs dependency metadata current, primarily for Go modules and GitHub Actions.

Important APIs and fields: It defines update ecosystems, directories, schedules, and possibly grouping or reviewer settings.

Control flow and state: Dependabot periodically opens pull requests; no repository runtime state is changed by the file itself.

Dependencies and integration points: Integrates with GitHub dependency scanning, `go.mod`, and workflow action versions.

Risks and test signals: Risks include noisy updates or missed security patches if schedules/directories drift. Signals are Dependabot PRs that pass CI and keep module/action versions current.
