# sources/object-store/minio-mc/cmd/client-fs_linux.go

## Purpose

`client-fs_linux.go` provides Linux-specific filesystem watch event mapping and xattr extraction for mc's filesystem backend. Linux is the richest platform here because inotify can report access/open events and xattrs can contain non-UTF-8 data.

## Important APIs, Control Flow, And State

`EventTypePut` maps to `InCloseWrite | InMovedTo`, delete maps to `InDelete | InDeleteSelf | InMovedFrom`, and get maps to `InAccess | InOpen`. `IsGetEvent`, `IsPutEvent`, and `IsDeleteEvent` scan the respective event slices for bit overlap. `getXAttr` reads a key and returns a UTF-8 string when valid, otherwise hex-encodes the raw value. `getAllXattrs` lists keys, skips `system.*` attributes, and returns nil rather than an error when xattrs are unsupported.

## Dependencies, Integration, Risks, And Tests

The file integrates with `fsClient.Watch` and preserve-mode metadata in `Get`/`Stat`. Dependencies are `notify`, `xattr`, `encoding/hex`, and UTF-8 validation. Key risks are event coalescing semantics from inotify, read/open events producing noisy watch output, and lossy user expectations for binary xattrs because non-UTF-8 values are exposed as hex strings. Tests are indirect through filesystem listing/get/stat tests and any Linux watch or preserve-mode coverage.
