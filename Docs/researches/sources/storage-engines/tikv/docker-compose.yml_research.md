# sources/storage-engines/tikv/docker-compose.yml

## Purpose
Defines a local six-container TiKV cluster: three PD nodes and three TiKV nodes using nightly PingCAP images, persistent named volumes, health checks, and a bridge network.

## Important APIs, Types, and Functions
Services `pd1`, `pd2`, and `pd3` expose client and peer ports, share a static initial cluster string, persist data/logs, and use PD health endpoints. Services `tikv1`, `tikv2`, and `tikv3` depend on all PD health checks, expose TiKV server/status ports, advertise service DNS names, and persist data/logs.

## Control Flow
Compose starts PD nodes together, waits for their health checks, then starts TiKV nodes. TiKV processes connect to all PD endpoints and advertise internal bridge-network hostnames for cluster communication. Health checks poll local PD/TiKV HTTP endpoints until ready.

## State and Persistence Behavior
Named Docker volumes retain PD metadata, TiKV data, and logs across container restarts. Removing volumes resets the cluster. Published host ports make the local cluster accessible outside the compose network.

## Dependencies and Integration Points
Requires Docker Compose, `pingcap/pd:nightly`, `pingcap/tikv:nightly`, container curl support, and available host ports 23791-23793, 23801-23803, 20161-20163, and 20181-20183. Useful for local integration testing against a real PD/TiKV topology.

## Risks
Nightly images are unstable and can change behavior without lockstep source updates. Static container names collide with other local deployments. Exposing status/client ports can leak operational data on shared hosts. Health checks assume `curl` exists in images.

## Test Signals
Run `docker compose up`, verify all six services become healthy, query PD health, and check TiKV `/status`. Validate restart behavior with named volumes and confirm cluster membership in PD after TiKV nodes join.
