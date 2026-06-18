
# sources/user-network-fs/rclone/fstest/testserver/images/test-sftp-openssh/Dockerfile

Purpose: minimal Alpine OpenSSH server image for SFTP integration tests.

Important APIs/types/functions: installs `openssh`, generates host keys, creates user `rclone`, sets password `password`, and runs `/usr/sbin/sshd -D`.

Control flow: image build prepares user/keys; container entrypoint starts sshd in foreground.

State/persistence: user and host keys are image-local. Test file data lives in the container filesystem unless volumes are added.

Dependencies/integration: used by `init.d/TestSFTPOpenssh`, which maps port 22 to a local test port and emits rclone SFTP config.

Risks: hard-coded password and no custom sshd hardening are test-only. Alpine `latest` can change behavior over time.

Test signals: successful TCP connection to mapped port and SFTP authentication as `rclone`.
