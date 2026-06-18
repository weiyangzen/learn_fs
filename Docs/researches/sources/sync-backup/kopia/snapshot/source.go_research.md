# sources/sync-backup/kopia/snapshot/source.go

Purpose: defines the canonical source identity for snapshots and parsing/string conversion for user-provided source selectors.

Important APIs/types/functions: `SourceInfo`, `SourceInfo.String`, and `ParseSourceInfo`.

Control flow: `String` renders empty source as `"(global)"`, host-only/user-host scopes as `user@host`, and path scopes as `user@host:path`. Parsing recognizes `"(global)"`, `user@host:path`, `@host`, `user@host`, and otherwise treats input as a local path that is absolutized and cleaned with the supplied default host/user.

State and persistence: no persistence here, but `SourceInfo` values are serialized into snapshot manifests and policy definitions.

Dependencies and integration points: used throughout snapshot listing, policy targeting, upload, maintenance, and source browsing.

Risks and test signals: parsing is simple delimiter-based and does not support usernames/hosts containing `@` or pathful selectors without `:`. Bare paths depend on process working directory. Tests cover round trips and invalid `"@"`.
