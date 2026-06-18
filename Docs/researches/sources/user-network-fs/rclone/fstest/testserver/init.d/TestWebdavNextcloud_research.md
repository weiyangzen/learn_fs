
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestWebdavNextcloud

Purpose: starts a Nextcloud container for WebDAV backend tests.

Important APIs/types/functions: sets SQLite DB, admin user/password, trusted domains, maps port `28629`, and emits WebDAV files URL for user `rclone` with vendor `nextcloud`.

Control flow: Docker run followed by config echo and `_connect`.

State/persistence: disposable container state.

Dependencies/integration: `nextcloud:latest`, Docker lifecycle, WebDAV tests.

Risks: `latest` image startup/API behavior can drift. `_connect` only checks TCP, not that Nextcloud initialization is fully complete.

Test signals: connect probe and successful WebDAV authentication/listing.
