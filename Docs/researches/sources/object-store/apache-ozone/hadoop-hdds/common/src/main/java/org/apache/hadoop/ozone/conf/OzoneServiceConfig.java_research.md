# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/conf/OzoneServiceConfig.java

## Purpose

`OzoneServiceConfig` defines service-level configuration shared by Ozone services, currently focused on shutdown-hook timeout behavior.

## APIs and control flow

The class is annotated `@ConfigGroup(prefix = "ozone.service")`. It exposes constants for minimum shutdown timeout, default time unit, default hook priority, and the `ozone.service.shutdown.timeout` key with default `60s`. The configured field is annotated as a time config tagged for Ozone, OM, SCM, datanode, Recon, and S3 Gateway. Getters and setters expose the resolved timeout in seconds.

## State, dependencies, and integration

State is the mutable `serviceShutdownTimeout` field populated by the HDDS configuration framework. The class depends on HDDS `@Config`, `@ConfigGroup`, `ConfigType`, and config tags. `ShutdownHookManager` and `HddsUtils.getShutDownTimeOut` use these values to bound hook execution and executor termination.

## Risks and test signals

The description string has no space between sentences, but runtime behavior is unaffected. Tests should cover default binding, parsing of time units, minimum timeout enforcement in consumers, and compatibility across all service tags.
