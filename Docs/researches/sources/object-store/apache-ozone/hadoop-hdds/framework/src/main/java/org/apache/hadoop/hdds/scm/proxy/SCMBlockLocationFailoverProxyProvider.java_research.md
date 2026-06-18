# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMBlockLocationFailoverProxyProvider.java

## Purpose
This class specializes the generic SCM failover proxy provider for the block-location protobuf protocol.

## Important APIs, Types, And Functions
The constructor calls `SCMFailoverProxyProviderBase` with `ScmBlockLocationProtocolPB.class`, the configuration source, and no explicit UGI. `getLogger()` returns the class logger. `getProtocolAddress(SCMNodeInfo)` selects `getBlockClientAddress()`.

## Control Flow
All meaningful proxy creation, retry, and failover behavior is inherited. This class only chooses which SCM endpoint field should be used for block client RPC.

## State, Persistence, And Dependencies
No extra state is introduced beyond the base class. It depends on SCM node info and the block PB interface.

## Integration Points
`ScmBlockLocationProtocolClientSideTranslatorPB` uses this provider to create a retry proxy for block allocation and deletion calls.

## Risks
Incorrect block-client address configuration prevents proxy construction. Because no UGI is passed, the base class uses the current user.

## Test Signals
Tests should assert that block client addresses are loaded and that inherited failover can cycle between block protocol endpoints.
