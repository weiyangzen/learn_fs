# sources/user-network-fs/rclone/backend/ulozto/ulozto_test.go

Purpose: Uloz.to backend tests. Runs generic rclone integration and specifically verifies behavior when rclone-encoded description metadata is absent.

Important APIs: `TestIntegration` with `TestUlozto:` and `TestListWithoutMetadata`. The metadata test uses `fstest.RandomRemoteName`, `fs.NewFs`, `fstests.PutTestContents`, `fstest.CheckListing`, private `Object.updateFileProperties`, and `operations.Purge`.

Control flow/state: upload a known payload, verify normal listing and hashes, clear the file description through `api.UpdateDescriptionRequest`, then ensure listing still succeeds with server mtime fallback and empty hashes. It then sets modtime and checks the new mtime is visible while hashes stay empty.

Dependencies/integration: configured `TestUlozto:` remote, rclone test helpers, backend internals, and Uloz.to live API behavior.

Risks/test signals: guards graceful degradation for files not uploaded by rclone or whose description was externally modified. Cleanup uses `operations.Purge`.
