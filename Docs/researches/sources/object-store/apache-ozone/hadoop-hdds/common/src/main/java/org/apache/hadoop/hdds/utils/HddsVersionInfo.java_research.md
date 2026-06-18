# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/HddsVersionInfo.java

## Purpose
Command-line and programmatic access to HDDS build/version metadata.

## Important APIs and types
Static `HDDS_VERSION_INFO` is a `VersionInfo("hdds")`. `main` prints version, source URL/revision, protoc versions, source checksum, compile platform, and debug containing jar.

## Control flow and state
No mutable state. Output is written to `System.out`; containing jar is logged only at debug level.

## Dependencies and integration points
Uses HDDS annotations for public/stable API, Hadoop `ClassUtil`, SLF4J, and the local `VersionInfo` class.

## Risks and test signals
Tests can assert output contains expected fields when build metadata resources are present. CLI output format may be consumed by scripts, so changes should be deliberate.
