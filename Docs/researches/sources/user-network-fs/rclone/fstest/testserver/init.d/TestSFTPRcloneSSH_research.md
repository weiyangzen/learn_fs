
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSFTPRcloneSSH

Purpose: starts `rclone serve sftp` and tests rclone's SFTP backend through an explicit `ssh` command using generated-on-start key files.

Important APIs/types/functions: writes a static OpenSSH private/public key pair to `/tmp`, starts `rclone serve sftp --authorized-keys`, and emits `type=sftp` plus an `ssh=ssh -i ... -p ... user@host` config line.

Control flow: key files are created/chmodded, server launches through `rclone-serve.bash`, and `_connect` is printed.

State/persistence: private/public keys remain under `/tmp/${NAME}.key(.pub)` unless cleaned manually; data/pid/log follow serve helper conventions.

Dependencies/integration: local `ssh` client behavior, rclone serve SFTP, and rclone SFTP backend's `ssh` option.

Risks: static private key material is embedded and written to `/tmp`; acceptable only for local tests. Long heredoc content makes maintenance awkward. Fixed port `28623` can conflict.

Test signals: TCP connect and successful SFTP operations through the custom ssh command.
