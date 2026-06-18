
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSFTPRclone

Purpose: starts `rclone serve sftp` with password authentication for SFTP integration tests.

Important APIs/types/functions: loopback port `28621`, fixed user/password, and `rclone-serve.bash` process/data management.

Control flow: `start` invokes `run rclone serve sftp --user --pass --addr`, then emits rclone SFTP config and `_connect`.

State/persistence: data under `/tmp/rclone-serve-sftp-data`; pid/log under `/tmp`.

Dependencies/integration: local rclone binary and testserver env setup.

Risks: fixed port and persistent `/tmp` data can interfere between abnormal runs.

Test signals: SFTP connection and operations against the rclone server.
