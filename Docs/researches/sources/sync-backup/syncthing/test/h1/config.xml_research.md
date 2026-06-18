# Research: sources/sync-backup/syncthing/test/h1/config.xml

## sources/sync-backup/syncthing/test/h1/config.xml

Purpose: integration fixture for host 1 in local Syncthing test clusters.

Important configuration: version 51; folder `default` at `s1`, basic filesystem, sendreceive, watcher enabled, puller/copy settings, two devices, GUI on `127.0.0.1:8081` with basic auth and API key `abc123`, listen addresses on TCP/QUIC port 22001, local announce enabled, global announce disabled, relays disabled, and defaults for folder/device templates.

Control flow: no executable flow, but tests load and sometimes rewrite this config before starting instance 1.

State and persistence: defines persistent home configuration for `h1`, plus default folder and option state used across tests.

Dependencies and integration: consumed by config loader and integration helpers. It pairs with h2/h3/h4 configs by device IDs and local ports. Risks include hard-coded ports, plaintext fixture API key, schema migration changing serialized fields, and tests that rename/restore this file. Test signals are broad: most integration tests start h1.
