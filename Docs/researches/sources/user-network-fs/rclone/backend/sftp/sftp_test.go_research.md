# sources/user-network-fs/rclone/backend/sftp/sftp_test.go

Purpose: external integration test entry points for the SFTP backend.

Important APIs/types/functions: `TestIntegration` runs against `TestSFTPOpenssh:`; `TestIntegration2` runs against `TestSFTPRclone:` unless a global `-remote` is supplied; `TestIntegration3` runs against `TestSFTPRcloneSSH:` under the same condition. All pass `NilObject: (*sftp.Object)(nil)` to `fstests.Run`.

Control flow: each test delegates to rclone's generic backend suite, which exercises filesystem semantics according to advertised backend features. The variants cover an OpenSSH server, rclone's SFTP server, and rclone over SSH configuration.

State and persistence behavior: relies on configured live remotes and may create/delete files on those remotes. It has no local state beyond test harness configuration.

Dependencies/integration: imports backend as an external package plus `fstest` and `fstests`. Build tag `!plan9` excludes unsupported platforms.

Risks/test signals: broad integration coverage for real SFTP behavior, but it depends on external fixtures and cannot pinpoint private helper regressions. It complements `sftp_internal_test.go` and `ssh_external_test.go`.
