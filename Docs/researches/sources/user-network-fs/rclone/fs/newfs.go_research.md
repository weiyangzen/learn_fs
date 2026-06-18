# sources/user-network-fs/rclone/fs/newfs.go

## Purpose
`newfs.go` constructs rclone filesystem backends from user paths. It parses remote strings, resolves backend registry entries and config maps, applies per-backend/global override parameters, tracks hashed config suffixes for remotes with extra connection-string config, and provides canonical config-string helpers.

## Important APIs, types, and functions
Exports include `WithRCRequest`, `IsRCRequest`, `NewFs`, `ConfigFs`, `ParseRemote`, `ConfigString`, `FullPath`, `ConfigStringFull`, and `TemporaryLocalFs`. Internal state includes `overriddenConfig` guarded by `overriddenConfigMu`, and `addConfigToContext` for `global.`/`override.` keys.

## Control flow
`NewFs` warns if a bare path matches a config section, calls `ConfigFs`, detects options overridden by connection-string config, computes a short base64 MD5 suffix like `{S_NHG}` when needed, stores suffix-to-config mapping, applies config overrides to context/global config, calls the backend `NewFs`, and registers reverse lookup when construction succeeds or returns `ErrorIsFile`. `ParseRemote` uses `fspath.Parse`, chooses local when no config name exists, reads configured remote type, or handles `:backend`.

## State and persistence behavior
The overridden-config suffix map is process-global and used later by `ConfigStringFull`. `global.` config overrides can mutate the process-wide background config unless the context is marked as an rc request. `TemporaryLocalFs` creates and removes a temp path before constructing a local fs there.

## Dependencies and integration points
This file integrates `fspath`, the backend registry (`Find`, `RegInfo.NewFs`), config maps/struct assignment, reverse fs registry helpers, global config options, and object path helpers. Every rclone command that opens a remote flows through this code.

## Risks and edge cases
Suffix generation must avoid collisions while producing filesystem-safe names for caches. `global.` options from normal contexts mutate global config, but rc requests must avoid cross-request leakage. Local paths can be confused with remote names, especially one-character names on Windows. `ConfigStringFull` depends on the in-memory suffix map being present.

## Test signals
`newfs_test.go` checks mock backend creation, suffix stability for equivalent extra params, canonical config strings, and global override mutation. `newfs_internal_test.go` checks override/global context behavior and rc isolation.

Source-read signal: reviewed complete local file (246 lines). Types observed: `rcRequestKeyType`. Functions/methods observed: `WithRCRequest`, `IsRCRequest`, `NewFs`, `addConfigToContext`, `ConfigFs`, `ParseRemote`, `configString`, `ConfigString`, `FullPath`, `ConfigStringFull`, `TemporaryLocalFs`.
