# sources/user-network-fs/rclone/fs/versiontag.go

## Purpose
This file defines the default base rclone version tag.

## Important APIs, State, Integration, and Risks
`VersionTag` is an exported package variable initialized to `"v1.75.0"`. It is combined with `VersionSuffix` by `version.go` to form `Version` when no full version is injected.

There is no control flow. The variable is mutable build/version state and can be overridden by release tooling. A stale tag or incorrect suffix combination would produce misleading CLI/version metadata. No direct tests are present in this subset; verification is normally through build artifacts or version command output.
