# sources/sync-backup/syncthing/lib/config/compression.go

## sources/sync-backup/syncthing/lib/config/compression.go

Purpose: Defines the configuration-level compression enum and translates it to wire-protocol compression values.

Important APIs/types/functions: `Compression` has `CompressionMetadata`, `CompressionNever`, and `CompressionAlways`. `MarshalText` and `UnmarshalText` support XML/JSON text encoding; `ToProtocol` maps to `protocol.Compression`.

Control flow and state: The type is stateless. `UnmarshalText` uses a lookup table that preserves legacy `"true"` and `"false"` values; unknown text falls through to the zero value, `CompressionMetadata`. `MarshalText` emits the current canonical strings.

Dependencies and integration: Used by `DeviceConfiguration.Compression` and later by connection/protocol setup through `ToProtocol`. It depends only on `lib/protocol`.

Risks and test signals: Unknown inputs silently become metadata compression rather than erroring, which is compatibility-friendly but can hide typos. `compression_test.go` checks legacy and canonical text conversions.
