## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/StorageContainerDatanodeProtocolClientSideTranslatorPB.java

Purpose: this client-side translator adapts the Java `StorageContainerDatanodeProtocol` interface to the protobuf RPC interface `StorageContainerDatanodeProtocolPB`.

Important APIs and types: it implements `StorageContainerDatanodeProtocol`, `ProtocolTranslator`, and `Closeable`. The central helper is `submitRequest(Type, Consumer<SCMDatanodeRequest.Builder>)`, which wraps a typed request and calls `rpcProxy.submitRequest`. Public methods implement `getVersion`, `sendHeartbeat`, and `register`.

Control flow and state: `NULL_RPC_CONTROLLER` is passed because Hadoop protobuf RPC does not use a controller here. `submitRequest()` sets the `cmdType`, lets the caller populate the matching payload, builds the wrapper, and unwraps `ServiceException` to an `IOException` through `ProtobufHelper.getRemoteException`. `register()` builds `SCMRegisterRequestProto` with extended datanode details, container report, pipeline reports, node report, and optional layout info.

Persistence and integration: no local persistence. It owns an RPC proxy and stops it in `close()`. It integrates with datanode endpoint state machines and SCM registration/heartbeat/version RPCs.

Risks and test signals: `getVersion()` ignores its request argument and sends an empty request, which is fine only if version requests have no fields. Response status is not checked locally; callers assume the server filled the requested response field. `SCMTestUtils.createEndpoint()` constructs this translator for test endpoint state machines.
