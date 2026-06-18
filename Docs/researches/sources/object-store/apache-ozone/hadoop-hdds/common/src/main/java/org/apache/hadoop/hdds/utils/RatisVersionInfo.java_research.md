# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/RatisVersionInfo.java

## Purpose
Loads and exposes build metadata for Apache Ratis as used by Ozone.

## Important APIs, Types, And Functions
The class owns a `Properties info` map loaded from `ratis-version.properties`. Public getters are `getVersion()`, `getRevision()`, and `getBuildVersion()`.

## Control Flow
The constructor resolves the resource through `ThreadUtil.getResourceAsStream`, loads it into `Properties`, and logs a warning on `IOException`. Getters return property values with `"Unknown"` fallbacks.

## State And Persistence
State is in-memory immutable-after-construction metadata. There is no write path; persistence is the packaged build-resource file.

## Dependencies And Integration Points
Depends on Hadoop `ThreadUtil` resource loading, Java `Properties`, and SLF4J. Consumers can use it in version banners, diagnostics, or endpoint metadata.

## Risks
If the resource is missing or unreadable, the object still constructs and silently degrades to `"Unknown"` values except for the warning. The constructor does not explicitly handle a null stream unless `ThreadUtil` throws or supplies a non-null stream.

## Test Signals
Tests should verify packaged resource loading, fallback values when the resource is unavailable, and formatting of `"version from revision"`.
