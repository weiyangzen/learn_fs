# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/conf/TestOzoneConfiguration.java

## Purpose
`TestOzoneConfiguration` is the main unit test for Ozone's configuration wrapper. It covers tagged property lookup, object injection and extraction, crypto compliance validation, resource inheritance, backward-compatible key fallback, post-construct validation, and tag recognition.

## APIs and dependencies
The tests use `OzoneConfiguration`, Hadoop `Configuration`, Hadoop `Path`, temporary XML resources, `LegacyHadoopConfigurationSource`, `SimpleConfiguration`, `ConfigTag`, SCM config constants, JUnit 5, and SLF4J logging callbacks.

## Control flow and state behavior
Helper methods write minimal Hadoop configuration XML files. `testGetAllPropertiesByTags` loads a default-like file with tag metadata and a site-like override file without tags, then verifies tag queries return overridden values. Object tests set typed properties, call `getObject`, and verify string, int, time, duration, class, and double conversion. Reverse tests call `setFromObject` and verify configuration values, including behavior for annotation defaults versus Java object defaults. Compliance tests set restricted or unrestricted crypto mode and assert whitelisted or disallowed signature algorithm behavior through both Ozone and legacy Hadoop views. Resource-instantiation tests confirm a source Hadoop configuration is preserved. Backward compatibility tests validate `getInt(newKey, fallbackKey, default, logger)` behavior. Validation tests assert invalid ports fail during object construction.

## Integration points
This class ties together `ozone-default.xml`, generated configuration metadata, Hadoop resource loading, annotation processing, legacy adapters, and compliance enforcement.

## Risks and test signals
The strongest risk areas are override semantics for tagged values, silent type-conversion changes, compliance whitelist enforcement, and fallback key behavior. These tests provide broad regression coverage for configuration compatibility and security-sensitive reads.
