<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/features.go -->
# sources/user-network-fs/rclone/fs/features.go

## Purpose
Centralizes optional filesystem capabilities and the interfaces backends implement to advertise them.

## Important APIs, Types, And Control Flow
`Features` contains boolean capability flags and function pointers for optional operations such as purge, server-side copy/move, directory metadata, change notify, wrapping, public links, unchecked/stream/chunked upload, recursive listing, quota, backend commands, disconnect, and shutdown. `Fill` detects optional interfaces on an `Fs`, stores methods, marks wrappers as overlays, and applies disabled-feature config. `Mask` intersects capabilities with another Fs for wrappers. `Wrap` and `WrapsFs` preserve wrapper relationships. `UnWrapFs`, `UnWrapObject`, and `UnWrapObjectInfo` peel wrapper layers.

## State And Persistence
Feature structs are in-memory descriptors with function pointers. They read `ConfigInfo.DisableFeatures` but do not persist data.

## Dependencies And Integration Points
Defines many public optional interfaces used by all backends and operations. It depends on core Fs/Object/Directory types, metadata, durations, listing callbacks, writer interfaces, and context.

## Risks And Test Signals
Reflection-based disable/list/enabled is string-name sensitive. Mask deliberately does not propagate some flags (`IsLocal`, `Overlay`) and keeps wrapper functions. Tests cover disable/list/enabled; broader behavior is exercised by backend integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/features.go -->
