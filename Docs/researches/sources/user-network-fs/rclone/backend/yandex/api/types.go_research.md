# sources/user-network-fs/rclone/backend/yandex/api/types.go

Purpose: JSON API types for the Yandex Disk backend plus sort-mode and API error helpers.

Important APIs: `DiskInfo`, `ResourceInfoRequestOptions`, `ResourceInfoResponse`, `ResourceListResponse`, `AsyncInfo`, `AsyncStatus`, `CustomPropertyResponse`, `SortMode`, and `ErrorResponse`. `SortMode` offers `Default`, `ByName`, `ByPath`, `ByCreated`, `ByModified`, `BySize`, `Reverse`, `String`, and `UnmarshalJSON`.

Control flow/state: structs are plain JSON containers. `SortMode` stores an unexported mode string, returns new values from builder methods, toggles leading `-` in `Reverse`, and manually unquotes JSON strings.

Dependencies/integration: standard `fmt` and `strings`; used by the Yandex backend for resource metadata/listing, async operation status, custom properties, and API errors.

Risks/test signals: manual JSON unquoting is less strict than `encoding/json` string decoding; no direct tests in this subset, so backend compile/integration tests are the signal.
