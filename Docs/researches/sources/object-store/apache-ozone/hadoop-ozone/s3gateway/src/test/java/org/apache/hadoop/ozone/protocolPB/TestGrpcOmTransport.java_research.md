
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/protocolPB/TestGrpcOmTransport.java

Purpose: unit tests for OM transport factory selection and gRPC transport lifecycle.

Important APIs and control flow: `setUp` configures Hadoop RPC protocol engine for `OzoneManagerProtocolPB`. `testGrpcOmTransportFactory` sets `OZONE_OM_TRANSPORT_CLASS` to `GrpcOmTransportFactory`, creates transport via `OmTransportFactory.create`, closes it, and asserts class simple name is `GrpcOmTransport`. `testHrpcOmTransportFactory` sets the Hadoop RPC factory and asserts the result is not gRPC. `testStartStop` instantiates `GrpcOmTransport`, starts it, and shuts it down in `finally`.

State, dependencies, integration: uses static `OzoneConfiguration` mutated across tests. Integrates OM protocol transport factories, Hadoop RPC engine, and current UGI.

Risks and test signals: shared mutable config means test order could matter if future tests add properties. It verifies factory wiring and start/stop smoke behavior, not real OM request traffic.
