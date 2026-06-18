# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/DatanodeSimulator.java

## Purpose
Vapor command that simulates many datanodes registering to SCM/Recon, heartbeating, and growing synthetic container state for scale testing.

## Important APIs, types, and functions
Command `simulate-datanode`, options for heartbeat threads, node count, containers per node, and reload. Uses `DatanodeSimulationState`, SCM/Recon datanode protocol translators, `StorageContainerLocationProtocol`, Ratis/SCM container allocation, HDDS layout version, Hadoop RPC, retry policies, JSON utils, and scheduled executors.

## Control flow
`call` initializes clients/layout, loads or creates simulated datanodes, registers each to SCM/Recon, schedules heartbeat tasks to every endpoint, installs a shutdown hook to stop executors, close clients, and save state, starts periodic stats logging, allocates containers until target assignment count is reached, closes each created container, then marks simulated nodes readonly and closes their pipelines.

## State and persistence behavior
Persists simulator state to `datanode-simulation.json` under the Ozone metadata directory on shutdown and reloads it by default. Runtime heartbeats maintain counters for total heartbeats/FCRs/ICRs.

## Dependencies and integration points
Exercises SCM datanode registration/heartbeat, Recon heartbeat, SCM container allocation/close APIs, layout storage/version manager, Hadoop protobuf RPC, HA SCM client creation, and Ozone metadata directory discovery.

## Risks and edge cases
Designed for stress environments and can create many SCM objects. Shutdown hook throws RuntimeException on interrupted await. Mixed real/simulated clusters may produce under-replicated synthetic containers. Random IPs may be unrealistic.

## Test signals
No direct tests. Runtime logs report registered node count, heartbeat/FCR/ICR rates, assigned container count, and readonly transition completion.
