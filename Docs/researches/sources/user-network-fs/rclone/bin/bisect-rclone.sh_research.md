# sources/user-network-fs/rclone/bin/bisect-rclone.sh

Purpose: example `git bisect run` helper for locating rclone regressions. It documents the bisect setup sequence, builds the current revision with `make`, prints `rclone version`, and leaves commented sample reproduction commands for backend copy/download failures.

State is the checked-out repository state controlled by git bisect. Dependencies are shell, `make`, and the locally built `rclone`. Compile failures exit `125` to mark revisions untestable. Risks include the script being checked into the repo and overwritten during bisect unless copied to `/tmp`, and the actual regression test must be manually edited in. No automated test exists because this is an operator template.
