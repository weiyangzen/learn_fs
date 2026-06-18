
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPVsftpdTLS

Purpose: starts an rclone-maintained vsftpd image variant intended for TLS-capable FTP testing.

Important APIs/types/functions: uses image `rclone/vsftpd`, fixed FTP user/password, `writing_mdtm=true`, and encoding flags.

Control flow: same as other Docker FTP scripts: run container, echo config, rely on shared lifecycle dispatcher.

State/persistence: disposable Docker container.

Dependencies/integration: `docker.bash`, `run.bash`, and `testserver.Start` consume the emitted config.

Risks: despite the name, this emitted config does not include explicit TLS options in the visible file; TLS behavior may be image default or configured elsewhere. Fixed credentials are test-only.

Test signals: connect probe on port 21 and integration test behavior against this server.
