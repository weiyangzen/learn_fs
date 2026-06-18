<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-shaded/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-shaded/pom.xml

## Purpose
Builds the shaded Ozone filesystem jar used by Hadoop 2 and Hadoop 3 filesystem compatibility artifacts.

## Important APIs, types, and functions
The module packages `ozone-filesystem-common` plus selected dependencies with relocations for many third-party packages. It excludes Hadoop-provided APIs, logging APIs, and selected native artifacts, uses `ServicesResourceTransformer`, unpacks Netty/Ratis native libraries, and renames native library files to match shaded prefixes.

## Control flow
The shade plugin runs during `package`, relocating `org`, `com`, `google`, `io`, `okio`, `okhttp3`, and other namespaces while excluding Hadoop/Ozone/logging/JDK-adjacent packages. The dependency plugin unpacks native dependencies during `validate`, and copy-rename runs during `generate-sources` to align native library names with relocated class names.

## State and persistence behavior
State is build output under `target/classes` and the shaded jar. Runtime persistence is not defined.

## Dependencies and integration points
This is a packaging boundary for filesystem clients that need Ozone dependencies without colliding with Hadoop distributions. It integrates with Ratis, Netty native transports/TLS, protobuf, and Maven shade relocation rules.

## Risks and test signals
The relocation pattern for `com` is intentionally broad due to a noted timeout issue, creating risk of unintended shading. Native library filtering/renaming is fragile across platform classifiers. Signals are Maven package, dependency conflict tests, client smoke tests on Linux/macOS architectures, and service loader validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-shaded/pom.xml -->
