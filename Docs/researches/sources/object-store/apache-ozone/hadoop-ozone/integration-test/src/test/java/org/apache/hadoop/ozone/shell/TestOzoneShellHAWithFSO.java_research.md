# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneShellHAWithFSO.java

Purpose: This subclass reruns the broad `TestOzoneShellHA` command suite with FILE_SYSTEM_OPTIMIZED as the default bucket layout. It verifies that the inherited shell, admin, trash, quota, replication, and delete workflows continue to work when new buckets default to FSO semantics.

Important APIs and types: It uses `OzoneConfiguration`, `OMConfigKeys.OZONE_DEFAULT_BUCKET_LAYOUT`, `OZONE_BUCKET_LAYOUT_FILE_SYSTEM_OPTIMIZED`, `OzoneConfigKeys.OZONE_HBASE_ENHANCEMENTS_ALLOWED`, `OZONE_FS_HSYNC_ENABLED`, and the inherited `startKMS` and `startCluster` hooks from `TestOzoneShellHA`.

Control flow: The overridden `@BeforeAll init` creates a fresh configuration, sets the default bucket layout to FSO, enables HBase-style enhancements and hsync on both server and client-facing keys, starts MiniKMS, and then starts the inherited HA cluster. All actual test methods are inherited unchanged.

State and persistence behavior: The persistent behavior under test is inherited OM/SCM/KMS state, but bucket creation without explicit layout now persists FSO layout metadata by default. This changes key namespace and trash behavior for inherited tests that omit `--layout`, while explicit OBS/LEGACY/FSO cases still set their own layout.

Dependencies and integration points: This class is an integration point between the generic Ozone shell HA suite and the FSO bucket-layout configuration path. It depends on the inherited static cluster lifecycle and KMS setup, so it must run as an isolated subclass instance rather than alongside a started base class.

Risks: Because almost all behavior is inherited, failures need to be interpreted as layout-sensitive regressions in the base shell workflows. Static fields in the parent class make lifecycle isolation important. The class does not add direct assertions that default-created buckets are FSO; it relies on inherited operations succeeding under the configured default.

Test signals: The signal is the full inherited `TestOzoneShellHA` suite passing with FSO default layout and hsync/HBase enhancements enabled.
