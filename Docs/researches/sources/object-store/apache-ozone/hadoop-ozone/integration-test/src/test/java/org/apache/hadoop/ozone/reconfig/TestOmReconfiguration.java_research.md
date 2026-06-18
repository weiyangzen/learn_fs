# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/reconfig/TestOmReconfiguration.java

## Purpose
`TestOmReconfiguration` validates live OM reconfiguration for admin/read-only admin lists, blacklist settings, list limits, deletion-service controls, and the snapshot SST filtering service interval.

## Important APIs, Types, and Functions
The subject is `cluster().getOzoneManager().getReconfigurationHandler()`. Expected properties combine OM admin keys, deletion interval/thread/limit keys, `OZONE_SNAPSHOT_SST_FILTERING_SERVICE_INTERVAL`, `OmConfig` reconfigurables, tracing config, and blacklist keys. Tests mutate properties through `reconfigureProperty` and inspect `OzoneManager`, `OmConfig`, `KeyManagerImpl`, deleting services, and SST filtering service handles.

## Control Flow, State, and Persistence
Each test updates one property and verifies the live OM object reflects the new value. Admin reconfiguration preserves the current user in the admin set. Blacklist group tests verify replacement rather than accumulation. Boolean parsing for list-all-volumes is tested with normal, empty, and invalid values. The SST filtering test changes the interval to `30s`, confirms the service stays enabled, changes it to `-1`, confirms the service stops and handle becomes null, then restores the original interval and confirms restart.

## Dependencies and Integration Points
This integrates OM reconfiguration, ACL/admin authorization config, key deletion and directory deletion services, `OmConfig`, tracing config, and snapshot SST filtering lifecycle management.

## Risks and Test Signals
Risks include expected key-set drift, service restart leaks, and parsing differences for empty/invalid booleans. The test provides direct signals through OM getters, service enablement flags, and active service references rather than just config strings.
