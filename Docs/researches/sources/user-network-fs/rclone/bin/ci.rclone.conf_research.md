# sources/user-network-fs/rclone/bin/ci.rclone.conf

Purpose: encrypted rclone configuration file for CI use. It contains the `RCLONE_ENCRYPT_V0` header and one encrypted blob, which rclone can decrypt with the appropriate config password/environment supplied in CI.

State and persistence are entirely the encrypted config payload. There are no functions or control flow in this file. Dependencies are rclone's encrypted config format and CI secret provisioning. Risks include config staleness, opaque credential scope, inability to review contents without secrets, and accidental exposure if the decrypting password is mishandled. Test signal is indirect: CI jobs depending on configured remotes will fail if this config cannot be decrypted or no longer works.
