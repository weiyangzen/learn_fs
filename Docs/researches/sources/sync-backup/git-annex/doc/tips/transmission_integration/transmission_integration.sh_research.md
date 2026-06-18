<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/tips/transmission_integration/transmission_integration.sh -->
# sources/sync-backup/git-annex/doc/tips/transmission_integration/transmission_integration.sh

Purpose: Transmission completion hook example that adds a finished torrent download to git-annex and commits it with a message containing Transmission environment details.

Control flow: `set -e`, verifies `TR_APP_VERSION` is set, builds a multiline commit message from `TR_APP_VERSION`, `TR_TIME_LOCALTIME`, `TR_TORRENT_DIR`, `TR_TORRENT_HASH`, `TR_TORRENT_ID`, and `TR_TORRENT_NAME`, prints it, changes to `$TR_TORRENT_DIR`, runs `git annex add "$TR_TORRENT_NAME"`, and commits with `git commit -F-` using the same message.

State and persistence: mutates the git-annex repository in the torrent directory by adding content and creating a Git commit.

Dependencies and integration points: Transmission script environment, Git, git-annex, and a repository rooted at or above `TR_TORRENT_DIR`.

Risks: the error message for missing `TR_APP_VERSION` expands the empty value rather than naming the variable. No locking is used, so concurrent torrent completions can race on the same repository. It assumes torrent name maps directly to a path under the torrent directory.

Test signals: run with a mocked Transmission environment in a temporary annex repo, verify add/commit, missing variable failure, duplicate/concurrent invocation behavior, and torrent names with spaces.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/tips/transmission_integration/transmission_integration.sh -->
