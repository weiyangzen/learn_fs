# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OzoneManagerProtocolPB.java

Purpose: Hadoop RPC protobuf binding for the main Ozone Manager client protocol.

Important APIs and types: Extends generated `OzoneManagerService.BlockingInterface`, declares protocol and Kerberos metadata, and advertises `OzoneDelegationTokenSelector` through `@TokenInfo`. Static `newProxy` helpers wrap OM failover providers in Hadoop `RetryProxy`.

Control flow: No request logic is implemented here. The two static helpers build retrying proxies using either a general OM failover provider or a follower-read failover provider with provider-supplied retry policies.

State and persistence behavior: Stateless interface. Persistent behavior is server-side OM request handling.

Dependencies and integration points: Used by Hadoop RPC transport, OM failover providers, client translator construction, delegation token selection, and secure RPC negotiation.

Risks: Protocol metadata and token selector are compatibility-sensitive. The static proxy helpers centralize retry wrapping; provider retry policies must remain compatible with read/write/follower-read semantics.

Test signals: Validate proxy creation for normal and follower-read providers, delegation-token service lookup, secure RPC principal use, and generated service method invocation.
