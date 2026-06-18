<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/configparse.go -->
# sources/user-network-fs/rclone/cmd/gitannex/configparse.go

## Purpose

`configparse.go` defines the git-annex special remote configuration keys and validates the rclone remote/backend value received from git-annex.

## Important APIs, Types, and Functions

`configID` identifies remote name, prefix, and layout values. `configDefinition` stores canonical names, synonyms, descriptions, and defaults. `requiredConfigs` defines `rcloneremotename/target`, `rcloneprefix/prefix`, and `rclonelayout/rclone_layout`. `getCanonicalName` and `fullDescription` format protocol responses. `validateRemoteName` accepts an exact configured remote, a remote fspath without path, or a colon-prefixed backend with options.

## Control Flow

Validation first checks configured remote names, then parses as fspath, rejects embedded path components, checks parsed remote names, and finally validates colon-prefixed backend names with `fs.Find`.

## State and Persistence Behavior

It reads configured remote names and backend registry only. No config is written.

## Dependencies and Integration Points

It integrates with git-annex config negotiation in `gitannex.go`, `fs/config`, `fspath.Parse`, and the rclone backend registry.

## Risks and Test Signals

Risks include accepting backend strings in user contexts, rejecting valid env-defined remotes if registry/config lookup changes, whitespace preservation surprises, and synonym drift with legacy git-annex-remote-rclone. Tests should cover exact remotes, env remotes, backends with options, nonexistent backends, embedded paths, and descriptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/configparse.go -->
