<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/test.sh -->
# sources/user-network-fs/rclone/cmd/test/info/test.sh

Source read: complete file, 51 lines, 1136 bytes, sha256 `1afe60f396e63edf8781b709bb2a8b118aec3009f56d506ba1968eaa1b16a284`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/test/info/test.sh_research.md`.

## Purpose
Zsh helper for running `rclone info` diagnostics across selectable remotes, suitable for parallel execution.

## Important APIs, types, and functions
Defines an associative array of remotes to extra flags, supports `--list`, sets local special-case config, purges the test directory, runs `rclone info -vv --write-json`, and captures logs/listing output.

## Control flow
For each remote, the script constructs a target directory, purges it best-effort, runs info, and then lists the directory into a `.list` file.

## State and persistence behavior
Writes `info-$remote.json`, `info-$remote.log`, and `info-$remote.list` in the current directory. Mutates/purges remote `infotest` directories.

## Dependencies and integration points
Depends on zsh, GOPATH layout, rclone binary, configured test remotes, and optional provider-specific environment variables such as `GCS_BUCKET`.

## Risks and edge cases
It is destructive for the chosen test directory and uses historical remote names/flags. Designed for manual diagnostics rather than CI.

## Test signals
Manual multi-provider data collection signal for `cmd/test/info`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/test.sh -->
