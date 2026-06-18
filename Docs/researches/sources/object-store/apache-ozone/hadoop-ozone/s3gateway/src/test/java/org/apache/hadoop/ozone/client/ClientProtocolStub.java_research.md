
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/ClientProtocolStub.java

Purpose: in-memory `ClientProtocol` implementation for S3 gateway unit tests, bridging `OzoneClientStub` and `ObjectStoreStub` to endpoint code that expects a full client protocol.

Important APIs and control flow: delegates active key paths to bucket stubs: create/rewrite key, create-if-absent, conditional rewrite, read/get/head key, delete key, multipart initiate/upload/complete/abort/list parts, directory creation, and object tagging. S3 object helpers use the default S3 volume. `getS3Secret` returns fixed stub credentials. Large portions of the interface return `null`, `false`, `0`, or no-op for unsupported volume, tenant, token, filesystem, ACL, snapshot, and transport operations.

State, dependencies, integration: stores only an `ObjectStoreStub` reference; actual state lives in volumes/buckets/keys. Integrated by `OzoneClientStub` constructor as the client proxy. Depends on a broad OM/client protocol API surface to satisfy compilation.

Risks and test signals: unsupported methods silently returning defaults can hide missing stub behavior in new tests. `getS3Secret` ignores the requested Kerberos ID and always returns constant credentials. Several methods intentionally do not mutate state, so endpoint tests using new code paths must extend the stub. Existing endpoint tests in this subset exercise key, multipart, tagging, and head/get paths through this class.
