# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAWithAllRunning.java

## Purpose
Standard OM HA integration tests where all OM nodes remain running. It covers object-store operations, client failover metadata, Ratis/JMX exposure, retry cache semantics, ACL behavior, link bucket ACL propagation, snapshots, and follower-read disabled fallback.

## Important APIs, types, and functions
- Extends `TestOzoneManagerHA` and uses common helpers from `AbstractOzoneManagerHATest` such as `setupBucket`, `createKey`, `testCreateFile`, and ACL helpers.
- Uses `HadoopRpcOMFailoverProxyProvider`, `HadoopRpcOMFollowerReadFailoverProxyProvider`, `OzoneManagerRatisServer`, `OMRatisHelper`, `OzoneManagerProtocolServerSideTranslatorPB`, `RaftServer`, and `RaftClientRequest`.
- Builds `OzoneObj` instances for bucket/key/prefix ACL operations and resolves link buckets back to source buckets for ACL equality.

## Control flow
Early tests validate recursive/non-recursive file creation, key deletion partial failures, volume and bucket CRUD, proxy initialization, suggested-leader exceptions, read failover to leader, JMX Ratis metrics, and retry-cache behavior by submitting duplicate Ratis requests with the same client/call id before and after cache expiry. ACL tests add/remove/set ACLs on buckets, keys, prefixes, and link buckets, then compare source/link ACL views. Ratis snapshot testing drives enough key writes to cross snapshot thresholds twice. The final test enables client follower-read against a cluster without follower-read support and expects fallback to leader-only reads.

## State and persistence behavior
The class creates HA-replicated volumes, buckets, keys, directories, prefixes, ACL entries, link buckets, retry-cache entries, and Ratis snapshots. Retry cache state is temporary and expires after configured duration. Snapshot index state is read from OM transaction info/Ratis state. ACL state must be stored against source buckets when link buckets are used.

## Dependencies and integration points
It integrates OM HA client routing, Ratis state machine submission, Hadoop UGI, Ozone object-store APIs, ACL authorizer data structures, JMX MBean server, Ratis application metrics, and link bucket source resolution.

## Risks and edge cases
Exact log/cache behavior and private retry-cache timing make the retry test sensitive. Link bucket ACL tests depend on recursive source resolution and default ACLs added by the RPC client. Snapshot tests depend on write volume and snapshot threshold configuration inherited from the HA harness.

## Test signals
Signals include expected `OMException` result codes, proxy map size/address matches, current proxy id equals leader id after read failover, MBean availability and nonnegative count, retry duplicate not re-executing before cache expiry, ACL list equality across link/source objects, and increasing Ratis snapshot indexes.
