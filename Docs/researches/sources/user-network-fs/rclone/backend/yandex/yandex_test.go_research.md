# sources/user-network-fs/rclone/backend/yandex/yandex_test.go

Purpose: declares the Yandex backend integration test entry point. `TestIntegration` calls `fstests.Run` with `RemoteName: "TestYandex:"` and a nil object typed as `*yandex.Object`, exercising the standard rclone backend contract against a configured live Yandex remote.

Control flow is intentionally minimal: the test package imports the backend under test and delegates all behavior checks to `fstest/fstests`, which will cover list, object create/update/read/delete, directory operations, metadata expectations, and optional features according to the backend capabilities. State is external: the test requires a configured `TestYandex:` remote and therefore depends on OAuth credentials and Yandex service availability. Risks are mainly coverage shape: it gives strong end-to-end signal when configured, but no local unit tests for REST error decoding, async job polling, custom modtime property behavior, or path encoding.
