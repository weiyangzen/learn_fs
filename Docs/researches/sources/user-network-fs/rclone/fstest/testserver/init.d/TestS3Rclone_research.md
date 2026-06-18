
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestS3Rclone

Purpose: starts `rclone serve s3` as a local S3-compatible test endpoint.

Important APIs/types/functions: uses `ACCESS_KEY_ID`, `SECRET_ACCESS_KEY`, loopback port `28624`, and `rclone-serve.bash`'s `run` helper.

Control flow: launches `rclone serve s3 --auth-key key,secret --addr`, then emits provider `Rclone`, endpoint, credentials, and `_connect`.

State/persistence: served data directory under `/tmp/rclone-serve-s3-data`; pid/log under `/tmp`.

Dependencies/integration: current rclone executable, serve helper, testserver env parser, S3 backend tests.

Risks: testing rclone S3 client against rclone S3 server can hide incompatibilities with third-party S3 services while still being valuable for protocol regression. Fixed port can conflict.

Test signals: local TCP connection and S3 operation results.
