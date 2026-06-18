# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/util/OzoneVersionInfo.java

Purpose: Public utility entry point that prints Ozone, protobuf, source, platform, Ratis, and HDDS build/version information.

Important APIs and types: Static `OZONE_VERSION_INFO`, `RATIS_VERSION_INFO`, ASCII `LOGO`, and `main(String[])`. It uses `VersionInfo`, `RatisVersionInfo`, `HddsVersionInfo`, and `ClassUtil`.

Control flow: `main` prints logo/version/release, repository URL and revision, protoc versions, source checksum, Ratis build version, compile platform, logs containing jar at debug level, then delegates to `HddsVersionInfo.main`.

State and persistence behavior: No state mutation or persistence. Reads build metadata from version-info resources/classes.

Dependencies and integration points: Used by command-line version output and diagnostics. Integrates Ozone and HDDS version metadata.

Risks: Output formatting is user-visible and may be asserted by scripts. Missing build metadata resources would produce incomplete version output through `VersionInfo`.

Test signals: CLI/version tests should assert key fields are present and delegation to HDDS version info does not fail.
