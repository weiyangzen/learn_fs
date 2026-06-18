# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/pom.xml

Purpose: This Maven module definition builds the `ozone-cli-debug` jar, a collection of developer/operator diagnostic commands for Ozone.

Important APIs and types: It declares artifact `org.apache.ozone:ozone-cli-debug:2.3.0-SNAPSHOT`, enables classpath generation, and depends on picocli, Jackson, Guava, Hadoop auth/common/HDFS, RocksDB JNI, SQLite JDBC, Ozone/Hdds modules, Recon, Ratis tools, JGraphT, and runtime logging/codec libraries.

Control flow: Maven resolves dependencies, runs the compiler with MetaInfServices and picocli Graal native-image annotation processors, and applies SpotBugs plus an enforcer rule overriding selected banned annotations/imports.

State and persistence behavior: The file persists build configuration and dependency graph. It does not define runtime state.

Dependencies and integration points: This module intentionally integrates with many Ozone internals: DB definitions, datanode container stores, OM/SCM metadata, Recon DBs, security auth, and CLI plugin discovery through `@MetaInfServices`.

Risks: The broad dependency set increases classpath conflict risk and makes the debug CLI sensitive to internal API changes. The explicit exclusion of Spring JDBC from Recon reduces transitive footprint. Annotation processor configuration is required for service metadata and native-image config generation.

Test signals: Maven compile/test/static-analysis success, generated service descriptors, and SpotBugs using the module exclude filter.
