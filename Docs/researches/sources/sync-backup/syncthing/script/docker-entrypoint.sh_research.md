# Research: sources/sync-backup/syncthing/script/docker-entrypoint.sh

## sources/sync-backup/syncthing/script/docker-entrypoint.sh

Purpose: container entrypoint that adjusts capabilities, ownership, umask, and user before launching Syncthing.

Important APIs/functions: shell checks for `UMASK`, root UID, `PCAP`, `PUID`, `PGID`, and `HOME`; uses `setcap`, `chown`, `su-exec`, and `exec`.

Control flow: sets umask if requested. When running as root, removes capabilities from the binary unless `PCAP` is set, otherwise applies requested capabilities, tries to chown home, then re-execs as `PUID:PGID` with HOME preserved. Non-root execution directly execs the command.

State and persistence: mutates binary capabilities and home directory ownership inside the container filesystem.

Dependencies and integration: Docker image runtime, Linux capabilities, `su-exec`. Risks include missing `PUID`/`PGID`, capability operations unavailable in restricted containers, and ignored chown failures. Test signal is container startup behavior.
