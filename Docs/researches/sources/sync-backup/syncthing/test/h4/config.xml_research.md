# Research: sources/sync-backup/syncthing/test/h4/config.xml

## sources/sync-backup/syncthing/test/h4/config.xml

Purpose: integration fixture for a fourth standalone host.

Important configuration: version 32; folder `default` at `s4/`, single device h4, basic filesystem, watcher disabled, auto-normalization disabled, puller pending limit 2048 KiB, GUI on `127.0.0.1:8084` with a distinct API key, listen includes dynamic relay endpoint and TCP 22004, local announce disabled, NAT disabled.

Control flow: configuration only. It is available for tests needing a separate single-device instance or normalization-specific behavior.

State and persistence: persistent fixture config under `h4`.

Dependencies and integration: config loader, integration helpers, local ports. Risks are hard-coded ports, older version migrations, and path trailing slash behavior. Test signal is indirect through any test that starts host 4.
