
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestS3Minio

Purpose: starts a Minio S3-compatible test server.

Important APIs/types/functions: defines fixed access/secret keys and port `28625`; `start` runs `minio/minio server /data` and emits rclone S3 provider `Minio` config.

Control flow: Docker start followed by config emission and `_connect`.

State/persistence: disposable container data under `/data`.

Dependencies/integration: Docker helper lifecycle and rclone S3 backend tests.

Risks: old Minio env names `MINIO_ACCESS_KEY`/`MINIO_SECRET_KEY` may differ in newer images. Fixed port can conflict.

Test signals: TCP connect to `127.0.0.1:28625` and S3 operation success.
