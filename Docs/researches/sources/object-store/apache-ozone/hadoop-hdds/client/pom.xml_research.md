# sources/object-store/apache-ozone/hadoop-hdds/client/pom.xml

Purpose: Maven module definition for the HDDS client library used by Apache Ozone clients to talk to storage containers and datanodes.

Important APIs/types/functions: The artifact is `hdds-client`. Dependencies include Guava, Jakarta annotations, commons-lang3, Hadoop common, HDDS common/config/erasurecode/interface-client, Ratis client/common/grpc/proto/thirdparty misc, SLF4J, and test utilities. Build plugins configure SpotBugs, the HDDS config annotation processor, and an enforcer rule banning `org.kohsuke.MetaInfServices`.

Control flow: During compilation, `ConfigFileGenerator` processes `@Config` classes such as `OzoneClientConfig` and `XceiverClientManager.ScmClientConfig`. SpotBugs uses the module filter. The enforcer override narrows allowed annotations/processors for this module.

State and persistence behavior: Produces the HDDS client jar and generated configuration metadata. No runtime state is in the POM.

Dependencies and integration points: This module is central to Ozone object-store clients, container protocol calls, Ratis/gRPC communication, and erasure-coded IO.

Risks: The dependency graph includes both Hadoop retry APIs and Ratis APIs; version drift can affect exception handling and wire behavior. The config annotation processor is required for documented config generation.

Test signals: Maven compile, config generation, SpotBugs, and client integration tests exercising Ratis/gRPC paths are key signals.
