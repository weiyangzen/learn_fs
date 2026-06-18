# sources/test-tools/strace/maint/gen-tag-message.sh

Purpose: constructs an annotated tag or release message from the top section of `NEWS` plus a contributor list.

Important APIs/types/functions: `get_commit_id`, `mktemp`, trap-based cleanup, `git show "$id:NEWS"`, sed extraction of the release marker, UTC date formatting, dynamic underline generation, and `gen-contributors-list.sh`.

Control flow: resolve commit argument or HEAD, copy that commit's NEWS to a temp file, extract the release version from the first `Noteworthy changes` marker, print a dated title and underline, print NEWS content until the next release marker, then append a fixed contributor intro and bulletized contributor names.

State and persistence behavior: uses a temporary NEWS copy removed on exit; no repository writes. Output embeds current UTC date, so it is intentionally time-dependent.

Dependencies and integration points: called by GitHub/GitLab/release-note wrappers and release tagging workflows. Depends on NEWS section format and git history.

Risks: malformed NEWS markers produce an empty version or wrong section. Date-sensitive output can make reproducible comparisons fail. Contributor generation inherits mailmap/trailer regex limitations.

Test signals: for a tagged release commit, the message should contain exactly the intended NEWS section, current release version, generated date, and contributors since previous `v*` tag.
