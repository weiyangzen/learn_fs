# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/TracingReconfigurationCallback.java

## Purpose

`TracingReconfigurationCallback` wires runtime configuration changes for `ozone.tracing.*` keys into HDDS tracing reinitialization. It is a narrow callback object intended to be registered with `ReconfigurationHandler`.

## Important APIs, Types, and Functions

`init(String, TracingConfig)` calls `TracingUtil.initTracing` once and returns the callback. `onPropertiesChanged(Map<String, Boolean>, Configuration)` scans changed keys for the `ozone.tracing.` prefix and calls `TracingUtil.reconfigureTracing`.

## Control Flow

Service startup calls `init`, then registers the returned object. After a reconfiguration completes, the handler supplies changed keys. This callback ignores non-tracing changes and only triggers tracing reconfigure when at least one changed property starts with the tracing prefix.

## State and Persistence Behavior

It keeps only `serviceName` and the mutable `TracingConfig` object reference. There is no direct persistence; the new configuration is supplied by the broader reconfiguration framework.

## Dependencies and Integration Points

It depends on `TracingUtil`, `TracingConfig`, and `ReconfigurationChangeCallback`. It expects tracing configuration binding to read refreshed values from the existing config object or backing configuration machinery.

## Risks and Test Signals

The `newConf` argument is not directly used, so correctness depends on how `TracingConfig` is backed. Prefix-only matching may reconfigure for any tracing key addition, update, or deletion. Tests should verify init is called once, non-tracing keys are ignored, and a tracing key deletion still triggers reconfiguration.
