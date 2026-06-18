
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPPureftpd

Purpose: starts a Pure-FTPd Docker test server and emits rclone FTP config.

Important APIs/types/functions: configures username/password/home, client/connection limits, passive port range, and encoding flags for Pure-FTPd behavior.

Control flow: `start` runs `stilliard/pure-ftpd`, then echoes `type=ftp`, Docker IP host, credentials, encoding settings, and `_connect`.

State/persistence: disposable Docker container with `/data` as FTP home inside the container.

Dependencies/integration: uses `docker.bash` and `run.bash`; consumed by `testserver.Start`.

Risks: passive ports are configured in the container environment but not explicitly published here, so tests rely on Docker networking behavior reachable from host/container context. External image drift can alter FTP behavior.

Test signals: port 21 probe and successful FTP backend operations.
