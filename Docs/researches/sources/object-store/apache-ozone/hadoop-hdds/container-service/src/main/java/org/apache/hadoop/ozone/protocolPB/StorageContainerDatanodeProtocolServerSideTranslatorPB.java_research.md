## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocolPB/StorageContainerDatanodeProtocolServerSideTranslatorPB.java

Purpose: this server-side translator receives protobuf RPC requests and forwards them to a Java `StorageContainerDatanodeProtocol` implementation.

Important APIs and types: it implements `StorageContainerDatanodeProtocolPB`, wraps an `OzoneProtocolMessageDispatcher<SCMDatanodeRequest, SCMDatanodeResponse, Type>`, and exposes `submitRequest`, `processMessage`, and a helper `register()`.

Control flow and state: `submitRequest()` delegates to the dispatcher with trace ID and command type. `processMessage()` switches on `Type`: `GetVersion`, `SendHeartbeat`, and `Register` each return an OK `SCMDatanodeResponse` with the corresponding implementation result. Unknown types throw `ServiceException`. `register()` extracts container, node, pipeline, and layout reports; if layout version is absent it supplies the initial layout version for backward compatibility.

Persistence and integration: no durable state. It integrates generated protobuf RPC, protocol metrics, logging, SCM implementation code, and upgrade layout compatibility helpers.

Risks and test signals: only three command types are supported in this translator; adding a new datanode protocol RPC requires updating both client and server switches. Exceptions from `IOException` and `TimeoutException` are wrapped as `ServiceException`. `SCMTestUtils.startScmRpcServer()` exercises this translator in tests.
