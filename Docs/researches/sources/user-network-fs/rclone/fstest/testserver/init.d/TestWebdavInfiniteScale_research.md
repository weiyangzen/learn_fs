
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestWebdavInfiniteScale

Purpose: starts ownCloud Infinite Scale (ocis) for WebDAV integration tests.

Important APIs/types/functions: prepares config directory `/tmp/ocis-config`, runs `owncloud/ocis init`, then starts ocis with basic auth enabled, insecure TLS, debug logging, and port `28639`. Emits WebDAV URL under the admin user's spaces path with vendor `infinitescale`.

Control flow: initialization container run, server container run, config echo with `_connect_delay=5s`.

State/persistence: config persists under `/tmp/ocis-config` between runs.

Dependencies/integration: Docker image `owncloud/ocis`, WebDAV backend tests, `docker.bash`.

Risks: persistent config plus forced overwrite can create surprising state. Uses insecure TLS and basic auth for tests. Fixed admin user id is embedded.

Test signals: HTTPS connect to port 28639 after delay and WebDAV operations.
