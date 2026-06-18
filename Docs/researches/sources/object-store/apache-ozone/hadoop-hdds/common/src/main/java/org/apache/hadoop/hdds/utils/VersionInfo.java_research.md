# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/VersionInfo.java

## Purpose
Loads build metadata for a named Hadoop/Ozone component from a packaged properties resource.

## Important APIs, Types, And Functions
`VersionInfo(String component)` loads `<component>-version-info.properties`. Getters expose release, version, revision, URL, source checksum, proto versions, compile platform, and formatted build version.

## Control Flow
The constructor opens the resource with `ThreadUtil.getResourceAsStream`, loads `Properties`, logs `IOException`, and closes through Hadoop `IOUtils.closeStream`. Getters use `"Unknown"` defaults.

## State And Persistence
State is an in-memory `Properties` object. The authoritative data is the build-time resource file.

## Dependencies And Integration Points
Annotated public/stable and used by component version singletons such as HDDS version information. Depends on Hadoop IO/resource utilities and SLF4J.

## Risks
Missing resources degrade to unknown values. The loaded keys must match build plugin output. Unlike `RatisVersionInfo`, this class exposes more fields and callers may assume non-unknown strings.

## Test Signals
Tests should verify real component property resources, fallback behavior, build-version formatting, and closing behavior for failed loads.
