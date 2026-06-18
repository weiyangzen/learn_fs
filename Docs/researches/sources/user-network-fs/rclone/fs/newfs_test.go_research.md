# sources/user-network-fs/rclone/fs/newfs_test.go

## Purpose
`newfs_test.go` validates public backend construction and canonical config-string behavior through the mock filesystem backend.

## Important APIs, types, and functions
The test exercises `fs.NewFs`, `ConfigString`, `ConfigStringFull`, `GetConfig`, and mock backend registration. It temporarily replaces `fs.Registry` to isolate registry state.

## Control flow
The test registers `mockfs`, creates a plain on-the-fly mock remote, creates equivalent remotes with extra `potato` config in boolean and quoted forms, verifies the hashed suffix name and full canonical config string, then creates a remote with `global.user_agent` and checks global config mutation without suffixing.

## State and persistence behavior
The test mutates global backend registry and global config user agent, restoring both with defers. It also populates the process-global overridden-config suffix map as part of `NewFs`.

## Dependencies and integration points
It depends on `fstest/mockfs`, backend registry behavior, config option override detection, fspath parsing, and config-string reconstruction.

## Risks and edge cases
The expected suffix `{S_NHG}` is tied to the hash/canonicalization of `potato='true'`; changing canonical option formatting will break this test. Global config restoration is manual.

## Test signals
Coverage confirms basic `:backend:path` creation, suffixing for extra config, equivalence of implicit boolean and quoted true, `ConfigStringFull` reversibility, and global override application.

Source-read signal: reviewed complete local file (62 lines). Functions/methods observed: `TestNewFs`.
