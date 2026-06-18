<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestGrpcOzoneManagerServer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestGrpcOzoneManagerServer.java

Purpose: Smoke test for `GrpcOzoneManagerServer` startup and shutdown.

Important APIs/types/functions: Mocks `OzoneManager`, obtains `OzoneManagerProtocolServerSideTranslatorPB`, delegation token manager, and certificate client from the mock, constructs `GrpcOzoneManagerServer`, then calls `start` and `stop`.

Control flow: The test creates default config and mock dependencies, starts the server inside a try block, and always stops it in `finally`.

State and persistence behavior: No OM persistence. It opens and closes server resources allocated by `GrpcOzoneManagerServer`.

Dependencies and integration points: Exercises gRPC OM server constructor/start/stop plumbing with protocol translator and security dependencies, but all OM dependencies are Mockito defaults unless explicitly stubbed elsewhere.

Risks: Because the OM mock is not stubbed, null translator/token/cert dependencies may be accepted by the server path under test; this is a lifecycle smoke test, not functional RPC coverage. It does not verify bound port, service registration, auth, or request handling.

Test signals: Passing indicates the gRPC server can tolerate the constructed dependency set and stop cleanly after start.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestGrpcOzoneManagerServer.java -->
