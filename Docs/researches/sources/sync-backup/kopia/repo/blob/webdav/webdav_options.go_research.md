# sources/sync-backup/kopia/repo/blob/webdav/webdav_options.go

Purpose: defines configuration for the WebDAV blob provider.

Important APIs/types/functions: `Options` contains WebDAV `URL`, `Username`, sensitive `Password`, optional trusted certificate fingerprint, `AtomicWrites`, and embedded `sharded.Options` plus `throttling.Limits`.

Control flow: `webdav_storage.go` consumes these options to create a `gowebdav.Client`, set identity encoding, optionally trust a single certificate fingerprint, choose sharded layout, and decide whether writes use a temporary random path or write directly.

State and persistence behavior: options are serialized in connection info; password is marked sensitive. Sharded options affect persisted file layout on the WebDAV server.

Dependencies/integration: shared with CLI/config paths and the WebDAV provider constructor.

Risks and edge cases: `AtomicWrites` trades compatibility for atomic visibility; when false, writes depend on server rename support.

Test signals: WebDAV tests exercise built-in and external servers, shard specs, credentials, connection-info round trips, and validation.
