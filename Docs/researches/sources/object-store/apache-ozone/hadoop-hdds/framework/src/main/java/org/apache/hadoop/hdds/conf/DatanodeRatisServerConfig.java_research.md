<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/DatanodeRatisServerConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/DatanodeRatisServerConfig.java

## Purpose
`DatanodeRatisServerConfig` declares typed configuration for datanode Ratis server behavior, timeouts, stream settings, log cleanup, pre-vote, and appender wait timing.

## Important APIs, Types, and Functions
It is annotated with `@ConfigGroup` for HDDS datanode Ratis plus Ratis server prefix. Config fields include request timeout, watch timeout, no-leader timeout, follower slowness timeout, pending request limit, datastream request threads, datastream client pool size, delete-Ratis-log-directory flag, pre-vote flag, and log appender minimum wait. Getters/setters expose each value, although the boolean setter for log directory cleanup is named `setLeaderNumPendingRequests(boolean)`.

## Control Flow
Runtime flow is config binding and later use by datanode/Ratis setup code. Duration setters convert to milliseconds.

## State and Persistence Behavior
The bean stores runtime config values; persistent values live in Ozone configuration files. Defaults are initialized in fields and annotations.

## Dependencies and Integration Points
It depends on HDDS config annotations/tags, `RatisHelper.HDDS_DATANODE_RATIS_PREFIX_KEY`, and Ratis `RaftServerConfigKeys.PREFIX`. It integrates with Ratis server construction and pipeline lifecycle behavior.

## Risks and Test Signals
Risks include setter name mismatch for `shouldDeleteRatisLogDirectory`, timeout relationships that can destabilize writes/watch behavior, and generated config metadata drift. Test signals include annotation processor output, config binding tests, Ratis pipeline creation/removal, pre-vote behavior, and datastream load tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/DatanodeRatisServerConfig.java -->
