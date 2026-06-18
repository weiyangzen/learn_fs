<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/all.sh -->
# sources/user-network-fs/rclone/cmd/test/info/all.sh

Source read: complete file, 16 lines, 445 bytes, sha256 `9aad378ec60258ac0f8e21dac309e55ac3ae206577d8f3a2a779e120eabc8e10`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/test/info/all.sh_research.md`.

## Purpose
Shell convenience wrapper for running the older `rclone info` checks across a fixed list of remotes.

## Important APIs, types, and functions
Execs `rclone --check-normalization=true --check-control=true --check-length=true info` with a local path and many `Test*:` remotes.

## Control flow
It replaces itself with the rclone process via `exec`; all behavior is delegated to the info command.

## State and persistence behavior
Remote test directories may be created or modified by the info command. The script itself writes no files.

## Dependencies and integration points
Depends on Bash, rclone in PATH, and configured test remotes.

## Risks and edge cases
Remote list includes historical names and may be stale. It is a manual helper, not robust orchestration.

## Test signals
Manual multi-remote signal for filename normalization/control/length support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/all.sh -->
