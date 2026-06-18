# sources/sync-backup/syncthing/lib/protocol/nativemodel_darwin.go

## Purpose
Darwin-specific raw model wrapper that converts incoming wire-format paths to macOS native Unicode normalization before model callbacks see them. Syncthing uses NFC on the wire, while macOS file names are handled as NFD internally.

## Important APIs, Types, and Functions
`makeNative` wraps a `rawModel` in `nativeModel`. `nativeModel.Index`, `IndexUpdate`, and `Request` rewrite `FileInfo.Name` or `Request.Name` through `norm.NFD.String` before delegating to the wrapped model.

## Control Flow
For index messages, the wrapper loops over the file slice in place and normalizes each name. For requests, it mutates the request name directly. After mutation, control passes to the embedded `rawModel` method.

## State and Persistence Behavior
No state is stored. The wrapper mutates message structs in memory before downstream handling, so callers must not rely on the original wire-normalized names after passing through this layer.

## Dependencies and Integration Points
Build-tagged for `darwin`; imports `golang.org/x/text/unicode/norm`. It is inserted by `NewConnection` before encryption/model delivery, making path normalization part of the BEP receive path.

## Risks and Edge Cases
In-place mutation means shared `FileInfo` slices could surprise tests or callers if reused. Correct behavior depends on the rest of the system using the same normalization convention for local filesystem paths. Only incoming model calls are handled here; outgoing conversion is handled by adjacent protocol/wire layers.

## Test Signals
There is no direct Darwin test in this subset. Cross-platform behavior is indirectly covered by scanner normalization and platform-specific protocol tests run on Darwin builders.
