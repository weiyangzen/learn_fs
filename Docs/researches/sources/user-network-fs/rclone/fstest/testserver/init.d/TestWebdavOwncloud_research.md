
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestWebdavOwncloud

Purpose: starts ownCloud Server for WebDAV integration tests.

Important APIs/types/functions: maps port `38081`, sets SQLite, admin credentials, trusted domain, disables Redis, and emits `/remote.php/webdav/` URL with vendor `owncloud`.

Control flow: Docker run, config emission, lifecycle via Docker helper.

State/persistence: disposable container state.

Dependencies/integration: `owncloud/server` Docker image and WebDAV backend.

Risks: hard-coded `OWNCLOUD_DOMAIN=localhost:8080` differs from mapped port and may be tolerated only because trusted domains includes 127.0.0.1. Fixed port is outside the nearby 286xx range.

Test signals: TCP connect to 38081 and WebDAV operation results.
