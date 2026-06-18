# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsDatanodeClientProtocolServer.java

## Purpose
Hadoop protobuf RPC server exposing datanode client-side administrative protocols, specifically reconfiguration and optional disk balancer protocol.

## Important APIs, Types, And Functions
Constructor binds an `RPC.Server`, updates datanode client RPC port, and refreshes ACLs when Hadoop service authorization is enabled. Public APIs are `start`, `stop`, `join`, and `getClientRpcAddress`.

## Control Flow
Server creation sets protobuf RPC engines, reads handler/read-thread counts from config, builds a reconfigure protocol blocking service, starts the RPC server, and conditionally adds disk balancer PB protocol to the same server.

## State And Persistence
State is the bound `RPC.Server`, resolved client RPC address, and configuration reference. The datanode details object is updated with the bound port.

## Dependencies And Integration Points
Integrates with `ReconfigurationHandler`, `DiskBalancerProtocolServer`, Hadoop IPC, HDDS server utilities, ACL policy provider, and datanode details ports.

## Risks
Port/address resolution and ACL refresh must happen after bind. Stop catches and logs errors but does not propagate. Disk balancer is optional and null-safe.

## Test Signals
Signals include successful bind to configured or fallback address, datanode port update, reconfigure and disk balancer RPC calls, ACL refresh under authorization, and clean stop/join.
