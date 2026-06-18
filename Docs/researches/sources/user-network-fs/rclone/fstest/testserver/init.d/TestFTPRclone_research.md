
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPRclone

Purpose: starts `rclone serve ftp` against a local temp data directory for FTP backend integration tests.

Important APIs/types/functions: sets `NAME`, `USER`, `PASS`, loopback IP, port `28622`, and `start` calls helper `run rclone serve ftp --user --pass --addr`.

Control flow: `rclone-serve.bash` manages pidfile/data directory and sources `run.bash`; `start` launches the server if not already running and prints FTP config plus `_connect`.

State/persistence: data lives under `/tmp/rclone-serve-ftp-data`; pid/log files live under `/tmp`.

Dependencies/integration: depends on the current `rclone` binary in PATH and the shared serve/run helpers.

Risks: fixed port can conflict with another local process. Leftover pidfiles are handled, but stale data can persist in `/tmp`.

Test signals: TCP connection to `127.0.0.1:28622` and FTP test success.
