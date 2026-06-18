
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSeafile

Purpose: starts a Seafile 7+ docker-compose stack and creates a default library for rclone Seafile backend tests.

Important APIs/types/functions: exports compose environment including MySQL/admin credentials, loopback port `8087`, data root, version, and compose dir. `start` runs docker-compose, waits for HTTP 200, obtains auth token, creates default repo, and emits Seafile config.

Control flow: compose up, polling loop, token curl, default-repo curl, config echo. `stop` and `status` are custom compose-aware implementations.

State/persistence: data persists under `${SEAFILE_TEST_DATA}/${NAME}` (default `/tmp/seafile-test-data/seafile7`), unlike most disposable containers.

Dependencies/integration: requires `docker-compose`, compose file in `init.d/seafile`, curl, and Seafile API.

Risks: persistent data can leak between runs; `latest` image drift can break startup/API. Token parsing via sed assumes exact JSON shape.

Test signals: HTTP connect to port 8087 and successful library access.
