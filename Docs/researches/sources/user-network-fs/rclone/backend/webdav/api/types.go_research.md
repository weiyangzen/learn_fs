# sources/user-network-fs/rclone/backend/webdav/api/types.go

Purpose: XML response contracts and helpers for WebDAV multistatus, properties, errors, time values, and quota.

Important APIs: `Multistatus`, `Response`, `Prop`, `PropValue`, `Error`, custom `Time`, `Quota`; methods `Prop.Code`, `Prop.StatusOK`, `Prop.Hashes`, `Error.Error`, and XML marshal/unmarshal for `Time`.

Control flow/state: `StatusOK` accepts any 2xx propstat and treats missing statuses as OK. `Hashes` extracts ownCloud/Nextcloud checksum strings or Fastmail SHA1. Time parsing tries several server formats and logs only once before falling back to epoch.

Dependencies/integration: XML/regex/string/time/sync plus rclone `fs` and `hash`. Consumed by `webdav.go` metadata/list/quota/error handling.

Risks/test signals: flattened propstat representation is lossy; epoch fallback can mask server time issues. `types_test.go` covers mixed-status behavior.
