# sources/storage-engines/wiredtiger/tools/antithesis/docker-compose.yaml

## Purpose
This Compose file defines the Antithesis test environment for a single WiredTiger `test/format` container. It gives the workload a fixed network identity, bind-mounted configuration, and persistent local data directory.

## Important services and fields
The `wiredtiger` service uses container name and hostname `wiredtiger`, image `wt-test-format:wt-latest`, and command `/bin/bash /opt/bin/test.sh -c CONFIG.antithesis -h /data/RUNDIR -T bulk,txn,retain=50`. It mounts `./data/wiredtiger` to `/data/` and binds local `CONFIG.antithesis` over `/opt/bin/test/format/CONFIG.antithesis`. The `antithesis-net` bridge network uses subnet `10.20.20.0/24` and assigns the container `10.20.20.6`.

## Control flow and behavior
Compose itself starts the service with the provided command. The image tag is rewritten by `build_and_push_containers.sh` during CI packaging, changing `wt-latest` to the selected Antithesis tag.

## State, dependencies, and integration
State persists in `./data/wiredtiger` on the host. The file depends on a built/pushed `wt-test-format` image and a local `CONFIG.antithesis` file. It integrates with Antithesis fault-injection assumptions by using a static low IPv4 address and comments that addresses `10.20.20.130` or higher are ignored by the fault injector.

## Risks and test signals
Risks include the mutable image tag, fixed container name/address collisions, host-directory permissions, and Compose version compatibility. Signals are container startup, `/data/RUNDIR` workload state, successful bind mount of `CONFIG.antithesis`, and reproducible network addressing for Antithesis orchestration.
