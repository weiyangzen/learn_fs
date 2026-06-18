# sources/sync-backup/syncthing/lib/protocol/nativemodel_unix.go

## Purpose
Default non-Windows, non-Darwin native model adapter. It is intentionally a no-op because normal Unix platforms use slash separators and NFC-compatible names matching Syncthing's wire format.

## Important APIs, Types, and Functions
`makeNative(m rawModel) rawModel` returns `m` unchanged.

## Control Flow
There is no wrapper and no conversion. Incoming index, request, cluster-config, close, and progress callbacks flow directly into the raw model.

## State and Persistence Behavior
No state exists and no message structs are mutated by this file.

## Dependencies and Integration Points
Build-tagged for `!windows && !darwin`; it fulfills the platform-specific `makeNative` symbol required by `NewConnection` in `protocol.go`.

## Risks and Edge Cases
The assumption is that the filesystem and higher layers already agree with wire-format path separators and normalization. Platforms that need special path handling must not match this build tag.

## Test Signals
Compile coverage on Unix builders verifies symbol availability. Protocol path validation tests in `protocol_test.go` exercise wire-format restrictions that this no-op adapter depends on.
