<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/pom.xml -->
# Research: sources/storage-engines/rocksdb/java/jmh/pom.xml

Purpose: Defines a Maven project that builds an executable JMH benchmark jar for the RocksDB Java API.

Important APIs/types/functions: Project coordinates are `org.rocksdb:rocksdbjni-jmh:1.0-SNAPSHOT`. Properties set Java source/target 17, UTF-8 encoding, JMH 1.22, and shaded jar classifier naming. Dependencies are `org.rocksdb:rocksdbjni:9.0.0`, `jmh-core`, and `jmh-generator-annprocess`. Plugins include `maven-compiler-plugin`, `license-maven-plugin`, and `maven-shade-plugin`.

Control flow: Maven compiles Java 17 benchmark sources with annotation processing, enforces license headers outside `pom.xml`, and shades dependencies into a runnable jar whose manifest main class is `org.openjdk.jmh.Main`. Signature metadata is stripped to avoid invalid signature errors in shaded artifacts.

State and persistence behavior: Build products land in Maven `target`. It does not use the local source tree's freshly built RocksDB JNI unless dependency resolution is overridden; by default it benchmarks RocksDB JNI version 9.0.0 from Maven repositories.

Dependencies and integration points: Integrates with JMH benchmark classes under `java/jmh/src/main/java`, Maven Central/local repository, license header file, and the RocksDB JNI binary dependency.

Risks and edge cases: The pinned RocksDB JNI dependency can lag the checked-out source version. JMH 1.22 is old relative to Java 17. License plugin strictness can fail generated or new files without headers.

Test signals: `mvn package` should produce the shaded benchmark jar; running it should list/execute the JMH benchmark classes. Dependency version mismatch is visible in benchmark logs and classpath resolution.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/pom.xml -->
