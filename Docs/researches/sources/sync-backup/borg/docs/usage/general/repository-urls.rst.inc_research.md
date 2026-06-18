# sources/sync-backup/borg/docs/usage/general/repository-urls.rst.inc

Purpose: documents accepted repository URL/path forms.

Important APIs and control flow: supports local paths and `file://`; SSH REST-over-stdio `rest://`; legacy Borg RPC `ssh://`; `sftp://`; `rclone:remote:path`; and `(s3|b2):.../bucket/path` object storage URLs. Double slash after host denotes absolute remote path; single slash denotes relative path.

State and persistence: URL choice controls where repository objects and locks live and which credentials/transports are used.

Dependencies and integration points: transport layers, `borg serve`, borgstore backends, rclone, boto3/S3/B2 credentials, SSH user/port parsing, and `BORG_REPO`.

Risks: absolute versus relative remote URL syntax is easy to misread. Some S3-compatible services require `b2:` due to known compatibility issues. Credentials embedded in URLs can leak.

Test signals: parser tests for every URL family, absolute/relative remote path behavior, optional user/port parsing, BORG_REPO defaulting, and backend-specific smoke tests.
