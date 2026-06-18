# File Research: sources/virtualization/guestfs-tools/bugs-in-changelog.sh

## Scope

Maintainer release-note helper that extracts referenced bugs/issues from git history for a supplied commit range.

## Behavior

- Requires one argument: a git commit range.
- Extracts Red Hat Bugzilla IDs and URLs from `git log`, normalizes to numeric IDs, sorts uniquely, and queries Bugzilla.
- Filters Bugzilla results to post-NEW/ASSIGNED states and emits POD `=item` entries with bug links and descriptions.
- Extracts Jira IDs matching `RHEL-[0-9]+` and GitHub guestfs-tools issue URLs, emitting placeholder `XXX` entries because it cannot fetch titles.

## Dependencies And Risks

- Requires `git`, `bugzilla` CLI, and Bugzilla login/API key.
- Empty bug sets or unauthenticated Bugzilla can cause misleading/truncated output.
- Output is POD fragment text intended for manual release note preparation.
