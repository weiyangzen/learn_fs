# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/reconfig/TestScmReconfiguration.java

## Purpose
`TestScmReconfiguration` validates live SCM reconfiguration for admin users, replication-manager settings, block deletion limits, safemode log interval, EC writable container provider settings, SCM config, and tracing config.

## Important APIs, Types, and Functions
The subject is `cluster().getStorageContainerManager().getReconfigurationHandler()`. Expected property sets include `OZONE_ADMINISTRATORS`, `OZONE_READONLY_ADMINISTRATORS`, `HDDS_SCM_SAFEMODE_LOG_INTERVAL`, `ReplicationManagerConfiguration`, `WritableECContainerProviderConfig`, `ScmConfig`, and `TracingConfig`. Behavioral tests inspect SCM admin sets, `ReplicationManagerConfiguration`, `SCMBlockDeletingService`, and SCM configuration values.

## Control Flow, State, and Persistence
Tests call `reconfigureProperty` or `reconfigurePropertyImpl` with new values and assert live SCM state changes immediately. Admin configuration includes current user for full admins and only the configured value for read-only admins. Replication interval and sample limit update the replication manager config object. Block deletion max updates the SCM block deleting service. Safemode log interval is checked in SCM configuration.

## Dependencies and Integration Points
This file integrates the reconfiguration framework with SCM authorization, replication manager, EC container provider config metadata, SCM block deletion, safemode logging, and tracing config.

## Risks and Test Signals
Risks include expected reconfigurable-property drift and differences between handler-level config updates and live service fields. Signals are direct live-object assertions, which catch reconfiguration hooks that update configuration text but not service behavior.
