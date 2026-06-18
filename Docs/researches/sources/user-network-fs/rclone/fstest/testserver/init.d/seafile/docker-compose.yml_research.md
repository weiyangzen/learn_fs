
# sources/user-network-fs/rclone/fstest/testserver/init.d/seafile/docker-compose.yml

Purpose: docker-compose stack used by Seafile testserver scripts.

Important APIs/types/functions: services are `db` (`mariadb:10.5`), `memcached`, and `seafile` (`seafileltd/seafile-mc:${SEAFILE_VERSION}`). Environment variables configure DB password, admin account, server hostname, and data volumes.

Control flow: compose starts DB and memcached before Seafile; Seafile maps `${SEAFILE_IP}:${SEAFILE_PORT}:80`.

State/persistence: MariaDB and Seafile data persist under `${SEAFILE_TEST_DATA}/${NAME}/...`.

Dependencies/integration: consumed by `TestSeafile` and `TestSeafileEncrypted` with project names and env vars.

Risks: compose file version 2.0 and older service images may require compatible docker-compose. Persistent volumes can retain stale users/libraries.

Test signals: Seafile scripts poll or sleep, then use the API to create libraries before tests.
