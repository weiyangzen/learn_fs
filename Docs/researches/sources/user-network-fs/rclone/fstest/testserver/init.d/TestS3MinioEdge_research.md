
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestS3MinioEdge

Purpose: starts Minio edge image to test rclone S3 behavior against a less stable/latest Minio line.

Important APIs/types/functions: same shape as `TestS3Minio`, but image `minio/minio:edge`, credentials differ, and port is `28626`.

Control flow: Docker run, emit S3 config, wait by `_connect`.

State/persistence: disposable container data.

Dependencies/integration: Docker and S3 tests; configured separately in `test_all/config.yaml`.

Risks: edge images can change or break without warning. Same credential-env compatibility risk as Minio stable.

Test signals: connection to port 28626 and S3 suite results.
