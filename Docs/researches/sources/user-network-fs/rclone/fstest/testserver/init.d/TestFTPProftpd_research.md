
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPProftpd

Purpose: starts a ProFTPD Docker container and emits rclone FTP remote config for integration tests.

Important APIs/types/functions: defines `NAME=proftpd`, user/password, sources `docker.bash`, and implements `start` with `docker run hauptmedia/proftpd`.

Control flow: `run.bash` dispatches `start`; the script starts the container, prints `type=ftp`, host from `docker_ip`, user, obscured password, encoding flags, and `_connect` probe.

State/persistence: container is disposable (`--rm`) and stopped by shared Docker helpers. Credentials are fixed test credentials.

Dependencies/integration: consumed by `testserver.Start`, which turns printed key/value lines into `RCLONE_CONFIG_TESTFTPPROFTPD_*` environment variables.

Risks: depends on external Docker image availability and Docker network IP inspection. FTP encoding expectations are server-specific.

Test signals: `_connect=<container-ip>:21` lets `testserver` wait until FTP accepts connections.
