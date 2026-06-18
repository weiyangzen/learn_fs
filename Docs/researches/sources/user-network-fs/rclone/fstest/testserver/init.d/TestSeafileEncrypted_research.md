
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSeafileEncrypted

Purpose: starts a Seafile stack and creates an encrypted library to test encrypted Seafile backend behavior.

Important APIs/types/functions: fixed encrypted library name/password, admin credentials, port `8088`, and `library_key` emitted obscured for rclone.

Control flow: compose up, fixed 60-second sleep, token retrieval, encrypted repo creation through API, config echo, custom compose stop/status.

State/persistence: data stored under `/tmp/seafile-test-data/seafile7encrypted` by default.

Dependencies/integration: docker-compose, Seafile API, curl, rclone obscure.

Risks: fixed sleep is less precise than polling. Persistent data and `latest` image drift can cause flaky repeated runs. Token sed parsing is brittle.

Test signals: connect probe on port 8088 and successful encrypted library operations.
