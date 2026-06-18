# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/StorageContainerLocationProtocolClientSideTranslatorPB.java

## Purpose
This class is the protobuf client-side implementation of `StorageContainerLocationProtocol`. It maps the large Java SCM container/admin API onto `ScmContainerLocationRequest` messages, applies HA routing rules, and converts responses into container, pipeline, admin, balancer, upgrade, token, and metrics domain objects.

## Important APIs, Types, And Functions
Constructors accept `SCMContainerLocationFailoverProxyProvider` and optional `ScmNodeTarget`. `submitRequest()` builds common wrappers with command type, client version, and trace ID. `submitRpcRequest()` routes follower-readable commands to a target SCM node when requested, sends admin commands to all SCM proxies, and sends ordinary commands through the retry proxy. The class implements allocation, lookup, listing, datanode admin, pipeline lifecycle, safe mode, replication manager, container balancer, datanode usage, upgrade finalization, container token, metrics, reconcile, and suppress APIs.

## Control Flow
Most methods validate inputs, build a command-specific protobuf request, call `submitRequest(Type, builderConsumer)`, and map the response. Allocation handles EC separately and sets factor one for backward compatibility. Listing combines optional state, type, replication config, and suppression filters. Admin commands are faned out across all proxies, retaining only the last response. Deprecated deleted-block methods return empty/zero; the deprecated factor-based list call throws unsupported.

## State, Persistence, And Dependencies
State is the retry proxy, failover provider, and optional target SCM node. There is no persistence. Dependencies are extensive: generated storage container protobufs, HDDS container/pipeline/datanode models, tracing, Hadoop `RetryProxy`/`RPC`, protobuf token helpers, Ozone upgrade status, and Apache Commons `Pair`.

## Integration Points
This is the main client translator for SCM admin and container operations. It depends on `StorageContainerLocationProtocolPB` for wire calls and `SCMContainerLocationFailoverProxyProvider` for HA. CLI tools and OM/admin callers exercise these methods.

## Risks
The class is broad and sensitive to protobuf field naming and command-type drift. Admin fan-out ignores all but the last response. `getExistContainerWithPipelinesInBatch()` swallows IO failures and returns an empty list. Some TODOs call out incomplete error handling. Follower targeting is limited to the command set declared in the protocol interface.

## Test Signals
Tests should verify every public method maps to the expected `Type` and request field, follower targeting and admin fan-out behavior, validation failures, EC versus replicated request encoding, safe-mode map conversion, balancer option validation, upgrade status conversion, token decoding, and unsupported deprecated calls.
