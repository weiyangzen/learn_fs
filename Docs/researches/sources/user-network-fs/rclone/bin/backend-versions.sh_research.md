# sources/user-network-fs/rclone/bin/backend-versions.sh

Purpose: release/documentation helper that inserts `versionIntroduced` metadata into backend documentation pages based on git history. It iterates top-level backend directories, skips special backends, finds the earliest relevant commit, finds the earliest version tag containing that commit, echoes backend/version, and uses `sed -i~` to insert front matter into `docs/content/<backend>.md`.

Dependencies are `bash`, `find`, `git`, `grep`, `sort`, and GNU/BSD-compatible `sed` behavior. State changes are direct edits to docs plus backup files. Risks include numeric `sort -n` being weak for semantic tags, insertion at fixed line 4 regardless of front matter shape, unquoted shell expansions around backend names, and creation of `~` backups. Test signal is manual; no automated test wraps this script.
