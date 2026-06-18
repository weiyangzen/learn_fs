
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSFTPOpenssh

Purpose: starts the OpenSSH SFTP Docker image and emits rclone SFTP config.

Important APIs/types/functions: maps local port `28627` to container port 22, uses user `rclone` and password `password`, and sets `copy_is_hardlink=true`.

Control flow: Docker run, config emission, `_connect` probe.

State/persistence: disposable container filesystem.

Dependencies/integration: image `rclone/test-sftp-openssh` and shared Docker lifecycle.

Risks: password-auth SFTP with fixed credentials is test-only. Hardlink copy behavior is server/filesystem-specific.

Test signals: SSH/SFTP connection to port 28627 and backend tests.
