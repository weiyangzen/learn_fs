# sources/user-network-fs/rclone/fs/version.go

## Purpose
This file builds the public `Version` string from compile-time version components.

## Important APIs, Flow, State, and Integration
`Version` is an exported package variable containing the complete rclone version string. During package initialization, if `Version` is empty, it is assigned from `VersionTag` alone or from `VersionTag + "-" + VersionSuffix` when `VersionSuffix` is non-empty.

The state is global and intentionally mutable at build/link time. It integrates with `versiontag.go`, `versionsuffix.go`, CLI version output, release builds, logging, and compatibility checks. Risks are mostly release-process related: injected `Version` skips default construction, an empty suffix suppresses the hyphen, and stale tag/suffix values produce misleading version output. There is no direct test in this subset.
