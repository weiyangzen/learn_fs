
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSeafileV6

Purpose: legacy Seafile v6-style single-container test server.

Important APIs/types/functions: sets port `8086`, admin credentials, data root, and image `seafileltd/seafile:${SEAFILE_VERSION}`. `start` runs Docker with `/shared` volume, sleeps, gets token, creates default library, and emits config.

Control flow: unlike newer compose scripts, uses `docker.bash` lifecycle. Startup waits by fixed 60-second sleep.

State/persistence: data persists under `/tmp/seafile-test-data/seafile6`.

Dependencies/integration: Docker, curl, Seafile v6 image/API, rclone obscure.

Risks: legacy image availability and API behavior may drift. Persistent data can affect idempotency.

Test signals: HTTP connection to port 8086 and default library operations.
