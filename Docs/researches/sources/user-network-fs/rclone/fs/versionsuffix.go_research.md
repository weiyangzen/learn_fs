# sources/user-network-fs/rclone/fs/versionsuffix.go

## Purpose
This file provides the default pre-release version suffix.

## Important APIs, State, Integration, and Risks
`VersionSuffix` is an exported package variable initialized to `"DEV"`. `version.go` appends it to `VersionTag` when constructing `Version`, unless `Version` is set directly or the suffix is overridden to empty.

There is no control flow. The variable is global package state intended for release tooling or linker flag override. If release automation fails to clear or replace it, release binaries may report a development-style version. No direct tests are present; behavior is visible through `fs.Version`.
