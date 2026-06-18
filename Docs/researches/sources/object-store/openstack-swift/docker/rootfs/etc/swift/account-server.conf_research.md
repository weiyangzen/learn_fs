# sources/object-store/openstack-swift/docker/rootfs/etc/swift/account-server.conf

## Purpose
Docker rootfs account-server config for a single containerized Swift node. It binds account service to `127.0.0.1:6202` and uses `/srv/node/`.

## Important Sections
Defaults set two workers, disabled mount check, and `LOG_LOCAL5`. Pipeline is `healthcheck recon account-server`, with account, recon, and healthcheck entry points. Account replicator, auditor, and reaper sections are present with defaults.

## Control Flow and Integration
Container startup scripts can run the account server and account background daemons using this file. It is simpler than SAIO multi-node configs because it targets one rootfs environment.

## State, Risks, and Test Signals
Account DBs persist under `/srv/node/accounts`. Risk is `mount_check = false`, appropriate for containers but unsafe if production expects mounted disks. Test signal is account service healthcheck and background daemon startup in Docker.
