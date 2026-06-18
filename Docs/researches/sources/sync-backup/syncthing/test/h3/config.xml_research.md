# Research: sources/sync-backup/syncthing/test/h3/config.xml

## sources/sync-backup/syncthing/test/h3/config.xml

Purpose: integration fixture for host 3 in multi-device and multi-folder cluster tests.

Important configuration: version 32; folder `default` at `s3` shared with h1/h2 and simple versioning keep=5; folder `s23` at `s23-3` shared with h2/h3; device entries for h1, h2, h3; GUI on `127.0.0.1:8083`; listen includes dynamic relay endpoint and TCP 22003; local announce and NAT disabled.

Control flow: no executable flow; consumed by integration startup helpers.

State and persistence: fixture home config for host 3, including multiple folders and simple versioning.

Dependencies and integration: used especially by `TestSyncCluster`; coordinates folder IDs including default and `s23`. Risks include older config version migrations, relay endpoint changes, and multi-folder schema drift. Test signal is three-node cluster convergence.
