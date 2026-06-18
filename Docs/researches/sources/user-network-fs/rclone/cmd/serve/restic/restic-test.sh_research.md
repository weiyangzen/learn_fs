<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic-test.sh -->
# sources/user-network-fs/rclone/cmd/serve/restic/restic-test.sh

Source read: complete file, 36 lines, 606 bytes, sha256 `79c2cf63263c391000670de30adb7e5693171bebc45bb41f38116823dd8d00a8`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/restic-test.sh_research.md`.

## Purpose
Shell helper for manually running restic serve integration tests against many configured rclone remotes.

## Important APIs, types, and functions
Defines a list of `Test*:` remotes, loops over them, runs `go test -remote $remote -v -timeout 30m`, tees per-remote logs, and prints ISO timestamps.

## Control flow
Executed manually from the restic serve package directory, commonly inside screen according to the comment.

## State and persistence behavior
Writes `restic-test.$remote.log` files in the current directory. It does not clean them or manage remote state beyond whatever the tests do.

## Dependencies and integration points
Depends on Bash, `go test`, configured rclone test remotes, and package test flags.

## Risks and edge cases
Assumes remote names are configured and that log filenames with colons are acceptable on the platform. It is not used by normal `go test`.

## Test signals
Manual broad compatibility signal across providers; not an automated unit-test input.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic-test.sh -->
