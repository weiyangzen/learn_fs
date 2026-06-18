# sources/object-store/openstack-swift/docker/rootfs/etc/swift/container-server.conf

## Purpose
Docker rootfs container-server config binding `127.0.0.1:6201` with storage under `/srv/node/`.

## Important Sections
Defaults set two workers, disabled mount check, and `LOG_LOCAL4`. Pipeline is `healthcheck recon container-server`. Background sections include replicator, updater, auditor, and sync.

## Control Flow and Integration
The container image uses this config for the container service and maintenance daemons. It omits the SAIO sharder tuning and node-specific loopback IPs.

## State, Risks, and Test Signals
Container DBs persist under `/srv/node/containers`. Risk is that disabled mount checks allow writing to the root filesystem if volume mounts are missing. Test signal is container service startup, healthcheck, recon, and updater/replicator operation in Docker.
