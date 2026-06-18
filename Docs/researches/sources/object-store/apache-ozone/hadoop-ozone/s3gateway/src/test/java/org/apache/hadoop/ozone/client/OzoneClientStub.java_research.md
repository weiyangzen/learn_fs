
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneClientStub.java

Purpose: test `OzoneClient` backed by in-memory object store and protocol stubs.

Important APIs and control flow: default constructor creates an `ObjectStoreStub`; main constructor passes object store and `ClientProtocolStub` to the superclass and initializes S3 gateway metrics. `close` is a no-op.

State, dependencies, integration: state is owned by the supplied `ObjectStoreStub`. Used throughout endpoint tests via `EndpointBuilder`.

Risks and test signals: metrics creation is global/static and can leak between tests if not handled by the metrics implementation. No-op close means resource lifecycle is not tested. Nearly every endpoint test in this subset uses this client.
