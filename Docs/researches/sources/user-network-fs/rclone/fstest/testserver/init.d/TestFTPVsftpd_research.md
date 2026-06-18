
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestFTPVsftpd

Purpose: starts a vsftpd Docker server for FTP integration tests.

Important APIs/types/functions: runs `fauria/vsftpd` with `FTP_USER` and `FTP_PASS`, then emits rclone FTP config including `writing_mdtm=true` and encoding flags.

Control flow: Docker start followed by environment output; lifecycle is delegated to `docker.bash`/`run.bash`.

State/persistence: disposable container state only.

Dependencies/integration: used by `testserver.Start` for remote `TestFTPVsftpd`.

Risks: external image behavior and Docker IP availability. FTP timestamp behavior is explicitly enabled, so backend tests may reveal server differences.

Test signals: `_connect` FTP port and successful rclone FTP operations.
