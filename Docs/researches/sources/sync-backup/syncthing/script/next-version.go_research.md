# Research: sources/sync-backup/syncthing/script/next-version.go

## sources/sync-backup/syncthing/script/next-version.go

Purpose: release helper that computes the next Syncthing semver tag.

Important APIs/functions: flag `-pre`, constant `suffix = "rc"`, helper `cmd`, and dependency `github.com/coreos/go-semver/semver`.

Control flow: finds latest tag and latest stable tag using `git describe`, parses both, scans commit subjects since latest stable for `feat` prefix to choose minor versus patch, handles stable release from an existing prerelease, increments prerelease counters when appropriate, or emits a new `rc.1`.

State and persistence: read-only Git history/tag inspection; output is printed tag string.

Dependencies and integration: Git tag naming convention `v[0-9].*`, semver library, release process. Risks include relying only on subject prefix for feature detection, prerelease parsing assumptions, and shallow clone tag availability. Test signal is command output under representative tag histories.
