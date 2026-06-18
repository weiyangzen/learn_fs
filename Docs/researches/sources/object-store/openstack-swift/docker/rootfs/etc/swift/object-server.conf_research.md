# sources/object-store/openstack-swift/docker/rootfs/etc/swift/object-server.conf

## Purpose
Docker rootfs object-server config binding `127.0.0.1:6200` with object storage under `/srv/node/`.

## Important Sections
Defaults set two workers, disabled mount check, and `LOG_LOCAL3`. Pipeline is `healthcheck recon object-server`. Object replicator, updater, and auditor sections are present.

## Control Flow and Integration
Object server and object maintenance daemons load this file inside the Docker rootfs. It is a compact single-node counterpart to the SAIO object configs.

## State, Risks, and Test Signals
Object data persists under `/srv/node/objects` or policy datadirs. Disabled mount checks are a container convenience but an operational risk. Test signal is object PUT/GET/DELETE through the proxy and object daemon startup.
