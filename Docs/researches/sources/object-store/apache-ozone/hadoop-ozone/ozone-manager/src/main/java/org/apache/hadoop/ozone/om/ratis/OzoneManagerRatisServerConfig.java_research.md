# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerRatisServerConfig.java

## Purpose
`OzoneManagerRatisServerConfig` declares configuration metadata for selected OM Ratis server settings.

## Important APIs and Types
The class is annotated with `@ConfigGroup` under the OM HA Ratis server prefix. Fields declare `@Config` metadata for log appender minimum wait time, retry cache expiry, read option, and leader lease read setting.

## Control Flow
There are no methods in the visible source; configuration processing discovers fields and annotations through the Ozone configuration framework.

## State and Persistence Behavior
The class holds configuration default values and metadata, not runtime state. Actual values are loaded from configuration and applied elsewhere, especially in `OzoneManagerRatisServer.newRaftProperties`.

## Dependencies and Integration Points
It integrates with `OMConfigKeys`, `RaftServerConfigKeys`, and Ozone config tags/types. Operators use these keys to tune Ratis read semantics and retry-cache behavior.

## Risks and Edge Cases
Annotation keys must stay aligned with Ratis and OM config consumers. The read option text documents semantics where `DEFAULT` is leader-only/non-linearizable and `LINEARIZABLE` supports ReadIndex.

## Test Signals
Config generation tests and property-binding tests should ensure defaults, types, tags, and key names remain correct.
