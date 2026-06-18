# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/package-info.java

Purpose: Package-level architecture documentation for HDDS SCM client implementations.

Important APIs/types/functions: No executable code. The doc explains that the package contains container service clients, distinguishes Ratis and Standalone clients, says Ratis is used for writing data and Standalone/gRPC for reading, and points to `XceiverClientManager` and `XceiverClientSpi`.

Control flow: Not applicable.

State and persistence behavior: Documentation-only source.

Dependencies and integration points: Provides context for the classes in `org.apache.hadoop.hdds.scm`, including `XceiverClientRatis`, `XceiverClientGrpc`, `XceiverClientManager`, and metrics/config classes.

Risks: The text is somewhat dated because EC and datastream paths add nuance beyond simple Ratis-write/Standalone-read framing.

Test signals: Compile/Javadoc generation only.
