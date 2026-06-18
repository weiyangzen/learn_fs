
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestWebdavRclone

Purpose: starts `rclone serve webdav` for local WebDAV backend tests.

Important APIs/types/functions: fixed user/password, loopback port `28620`, `rclone-serve.bash` process/data management, and emitted vendor `rclone`.

Control flow: `start` runs `rclone serve webdav --user --pass --addr`, then echoes URL, credentials, and `_connect`.

State/persistence: data under `/tmp/rclone-serve-webdav-data`; pid/log under `/tmp`.

Dependencies/integration: current rclone binary and WebDAV backend tests.

Risks: client/server same-code testing can miss third-party WebDAV quirks. Fixed port and stale `/tmp` data risks.

Test signals: TCP connect and WebDAV operations.
