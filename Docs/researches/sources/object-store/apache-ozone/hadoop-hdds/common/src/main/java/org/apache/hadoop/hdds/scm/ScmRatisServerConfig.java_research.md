# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ScmRatisServerConfig.java

## Purpose
Defines typed config for one SCM HA Ratis server option: minimum wait time between appendEntries calls.

## Important APIs, Types, And Functions
`ScmRatisServerConfig` is annotated with `@ConfigGroup(prefix = ScmConfigKeys.OZONE_SCM_HA_PREFIX + "." + RaftServerConfigKeys.PREFIX)`. It has `logAppenderWaitTimeMin`, `getLogAppenderWaitTimeMin()`, and setter.

## Control Flow
The configuration framework binds the time value from `ozone.scm.ha.raft.server.log.appender.wait-time.min`.

## State And Persistence
The object stores in-memory config derived from external configuration; no direct persistence.

## Dependencies And Integration Points
Depends on HDDS config annotations and Ratis `RaftServerConfigKeys`. Integrated by SCM Ratis server initialization/performance tuning.

## Risks And Test Signals
Risk is unit mismatch because the field is a `long` configured as `ConfigType.TIME`. Tests should verify default conversion and that the value is applied to Ratis properties.
