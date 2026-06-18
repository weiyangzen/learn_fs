# sources/user-network-fs/rclone/backend/webdav/webdav_test.go

Purpose: live WebDAV integration test entry points for multiple vendors.

Important APIs: `TestIntegration` for Nextcloud with chunked upload config, `TestIntegration2` for ownCloud, `TestIntegration3` for rclone WebDAV, `TestIntegration4` for NTLM, and `SetUploadChunkSize`.

Control flow/state: each test delegates to `fstests.Run` with vendor remote names and `NilObject`. Some tests skip when an explicit `-remote` is set.

Dependencies/integration: rclone `fs`, `fstest`, `fstests`, and configured vendor remotes.

Risks/test signals: broad but environment-dependent contract coverage; Nextcloud chunked upload gets explicit minimum chunk-size coverage.
