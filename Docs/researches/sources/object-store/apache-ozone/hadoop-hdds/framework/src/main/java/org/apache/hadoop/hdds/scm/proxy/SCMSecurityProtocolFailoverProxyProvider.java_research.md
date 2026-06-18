# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMSecurityProtocolFailoverProxyProvider.java

## Purpose
This class adapts generic SCM failover to the SCM security protobuf protocol.

## Important APIs, Types, And Functions
The constructor passes `SCMSecurityProtocolPB.class`, configuration, and optional UGI to the base provider. `getProtocolAddress()` selects `SCMNodeInfo.getScmSecurityAddress()`.

## Control Flow
All runtime behavior is inherited. This class only binds the protocol type and security endpoint.

## State, Persistence, And Dependencies
No extra state exists. Dependencies include `SCMSecurityProtocolPB`, SCM node info, UGI, and logging.

## Integration Points
Certificate and security clients use this provider to communicate with SCM security endpoints in HA deployments.

## Risks
Security RPCs depend on correct security-address config and UGI. Any mismatch can block certificate/key operations.

## Test Signals
Tests should verify security address selection and inherited failover/retry behavior against security protocol proxies.
