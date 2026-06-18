# Research: sources/sync-backup/syncthing/test/h2/config.xml

## sources/sync-backup/syncthing/test/h2/config.xml

Purpose: integration fixture for host 2, usually syncing folder `default` with h1.

Important configuration: version 52; folder `default` at `s2`, watcher disabled, rescan interval 60 seconds, copiers 8, max concurrent writes 8, devices h1 and h2, GUI on `127.0.0.1:8082` without configured user/password, API key `abc123`, listen addresses TCP/QUIC port 22002, relay enabled, LAN bandwidth limiting enabled, and standard defaults.

Control flow: schema fixture only. Several tests temporarily rewrite folder versioning or append many devices through REST/config APIs.

State and persistence: persistent host home config and fixture defaults. Device IDs and ports coordinate with h1/h3.

Dependencies and integration: used by two-peer tests, HTTP GUI tests, conflict tests, file type/symlink/versioning tests, and many-peers configuration mutation. Risks include hard-coded ports and config version migrations. Test signal is successful startup and sync behavior.
