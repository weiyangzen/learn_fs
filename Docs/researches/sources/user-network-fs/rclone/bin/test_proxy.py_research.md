# sources/user-network-fs/rclone/bin/test_proxy.py

Purpose: sample dynamic backend proxy for rclone serve modes. It reads JSON credentials from stdin and returns an rclone remote config JSON for an SFTP backend on localhost, marking `pass` for obscuring.

State is pure stdin/stdout transformation. Dependencies are Python JSON and input fields `user` and `pass`. Risks include assuming localhost SFTP, passing credentials through process pipes, no validation, and only demonstrating a minimal config shape. Test signal is manual/demo use with rclone serve proxy functionality.
