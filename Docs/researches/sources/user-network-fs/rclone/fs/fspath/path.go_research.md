# sources/user-network-fs/rclone/fs/fspath/path.go

## Purpose
`path.go` parses and manipulates rclone filesystem paths. It distinguishes local paths from configured remotes and on-the-fly backend strings, validates remote/config names, parses comma-separated connection parameters, and supplies helpers for splitting and joining remote roots.

## Important APIs, types, and functions
Public APIs include `CheckConfigName`, `MakeConfigName`, `Parsed`, `Parse`, `SplitFs`, `Split`, and `JoinRootPath`. Important internal helpers include `checkRemoteName`, `isConfigParam`, `makeAbsolute`, regex matchers for config names, and explicit parser errors such as `errBadConfigParam`, `errQuotedValue`, and `errAfterQuote`.

## Control flow
`Parse` first treats strings without colons as local paths, then runs a state machine over config name, parameter, value, quoted value, after-quote, and done states. It supports `remote:path`, `:backend,param=value:path`, boolean params, single/double quoted params, doubled quote escaping, drive-letter detection, and slash conversion for parsed remote paths. `SplitFs` appends the remote colon back, `Split` uses `path.Split`, and `JoinRootPath` normalizes a candidate child path so it cannot climb above the root.

## State and persistence behavior
The file holds only compiled regexes and sentinel errors. It persists nothing; all parse results are returned as `Parsed` values with optional `configmap.Simple` maps.

## Dependencies and integration points
`newfs.go` calls `ParseRemote` through this package to resolve backends. Mount helpers and tests share similar quoting concepts. `JoinRootPath` is used by `fs.FullPath` and other places that reconstruct canonical `remote:path` strings. `driveletter.IsDriveLetter` handles Windows ambiguity.

## Risks and edge cases
Colons in local paths, Windows drive letters, leading `:backend` remotes, Unicode remote names, quoted parameter values, doubled quotes, empty params, and path traversal normalization are all sensitive. Remote names allow spaces internally but not leading/trailing space or leading hyphen. Parser behavior is part of rclone's user-facing CLI contract, so compatibility changes can break config strings.

## Test signals
`path_test.go` covers remote-name validation, Unicode names, on-the-fly backend params, quote escaping, local colon paths, Windows-specific slash/drive-letter cases, `SplitFs`, `Split`, `makeAbsolute`, and `JoinRootPath`. `fuzz.go` adds fuzz invariants.

Source-read signal: reviewed complete local file (356 lines). Types observed: `Parsed`. Functions/methods observed: `CheckConfigName`, `MakeConfigName`, `checkRemoteName`, `isConfigParam`, `Parse`, `SplitFs`, `Split`, `makeAbsolute`, `JoinRootPath`.
