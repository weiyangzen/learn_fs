# Research: sources/user-network-fs/rclone/fs/override.go

## sources/user-network-fs/rclone/fs/override.go

Purpose: defines `OverrideRemote`, a lightweight `ObjectInfo` wrapper that substitutes the `Remote()` and `String()` value while forwarding optional object capabilities. APIs include `NewOverrideRemote`, `Remote`, `String`, `MimeType`, `ID`, `UnWrap`, `GetTier`, and `Metadata`.

Control flow is straightforward delegation: construction unwraps an existing `OverrideRemote` to avoid wrapper stacking, while optional methods type-assert the embedded `ObjectInfo` to capability interfaces and return default empty or nil values when unsupported. State is only the embedded object info and replacement remote string; persistence is none. Dependencies are core fs interfaces such as `ObjectInfo`, `Object`, `MimeTyper`, `IDer`, `GetTierer`, and `Metadataer`. Integration points are operations that need to upload/copy data under a different destination name while preserving source metadata, hashes, size, and optional object behavior. Risks are subtle interface exposure changes: unsupported optional methods silently return empty values, and `UnWrap` only returns when the wrapped value is an `Object`, not arbitrary nested wrappers.
