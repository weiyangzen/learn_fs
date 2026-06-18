# sources/user-network-fs/rclone/bin/tidy-beta

Purpose: release maintenance script for deleting old beta artifacts from `beta.rclone.org:` matching a version prefix. It defaults to dry-run and requires a second argument `delete` to actually delete.

Control flow validates version argument, sets `--dry-run` unless deletion is confirmed, then runs `rclone delete` with progress, concurrency, fast-list, and include filters for root and branch beta paths. State changes are remote deletions only when confirmed. Dependencies are configured `beta.rclone.org:` remote and rclone. Risks include overly broad include patterns if version is wrong, remote credential scope, and dry-run output needing review before actual deletion. Test signal is dry-run listing and delete command success.
