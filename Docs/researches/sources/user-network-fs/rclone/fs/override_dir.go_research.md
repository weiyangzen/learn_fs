# Research: sources/user-network-fs/rclone/fs/override_dir.go

## sources/user-network-fs/rclone/fs/override_dir.go

Purpose: defines `OverrideDirectory`, a `Directory` wrapper that changes `Remote()` and `String()` while preserving all other directory behavior through embedding. APIs are `NewOverrideDirectory`, `Remote`, and `String`.

Control flow mirrors `OverrideRemote`: construction unwraps an existing `OverrideDirectory` to keep a single wrapper around the original `Directory`, then stores the new remote name. State is only the embedded directory and replacement remote string. There is no persistence or concurrency behavior. Dependencies are the fs `Directory` interface. Integration points include directory listing, sync, and metadata flows that need a directory entry to be presented at a different path without copying or reconstructing all fields. Risks are low but include identity confusion when callers compare string/remote names to underlying directory fields, and the fact that optional directory capabilities are not explicitly forwarded beyond what embedding already exposes.
