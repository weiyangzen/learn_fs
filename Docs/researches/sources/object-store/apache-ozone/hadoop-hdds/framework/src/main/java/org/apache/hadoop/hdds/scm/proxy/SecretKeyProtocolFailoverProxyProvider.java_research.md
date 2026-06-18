# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SecretKeyProtocolFailoverProxyProvider.java

## Purpose
This generic provider adapts SCM failover to protobuf secret-key protocol blocking interfaces.

## Important APIs, Types, And Functions
The class is parameterized as `<T extends SCMSecretKeyProtocolService.BlockingInterface>`. Its constructor accepts configuration, UGI, and the concrete proxy class, then delegates to the base provider. It selects `SCMNodeInfo.getScmSecurityAddress()` as the endpoint.

## Control Flow
Retry, proxy creation, and failover are inherited from `SCMFailoverProxyProviderBase`.

## State, Persistence, And Dependencies
No extra state exists. It depends on generated secret-key protobuf service interfaces, SCM node info, UGI, and logging.

## Integration Points
Secret-key clients use this provider to fetch current and historical symmetric keys from SCM security endpoints. `SingleSecretKeyProtocolProxyProvider` extends it to disable failover for a fixed SCM node.

## Risks
Generic typing must match the generated blocking interface used by the caller. It shares the same security endpoint as SCM security protocol, so config errors affect both.

## Test Signals
Tests should verify generic proxy construction, security address selection, failover behavior, and compatibility with concrete secret-key service interfaces.
