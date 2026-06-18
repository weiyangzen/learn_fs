# sources/object-store/apache-ozone/hadoop-hdds/server-scm/pom.xml

Purpose: Maven module descriptor for `hdds-server-scm`, defining dependencies, resources, annotation processors, static analysis, web/docs resource unpacking, and test protobuf generation.

Important APIs and types: Configures `maven-compiler-plugin`, `maven-enforcer-plugin`, `maven-dependency-plugin`, `spotbugs-maven-plugin`, and `protobuf-maven-plugin`.

Control flow: Compile runs Ozone config and replication annotation processors. `prepare-package` unpacks shared web assets and docs. `generate-test-sources` compiles test protobufs.

State and persistence behavior: Controls generated sources and packaged artifact contents, not runtime state directly.

Dependencies and integration points: Pulls together HDDS common/client/container/interface/framework modules, managed RocksDB, Ratis, Hadoop, protobuf, Jackson, Jetty, BouncyCastle, Guava, servlet APIs, runtime logging, and test jars.

Risks: Scope changes can break runtime packaging because some dependencies are compile-scope for transitive runtime needs. Replication annotations rely on processor configuration.

Test signals: Maven compile, test-compile, SpotBugs, and package phases validate this file.
