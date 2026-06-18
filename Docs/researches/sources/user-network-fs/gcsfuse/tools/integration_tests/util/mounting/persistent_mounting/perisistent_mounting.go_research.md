# sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/persistent_mounting/perisistent_mounting.go

Purpose: supports integration tests through the persistent mount helper path, translating CLI-style gcsfuse flags into `-o` options for `mount.gcsfuse`.

Important APIs/types/functions: `makePersistentMountingArgs`, `mountGcsfuseWithPersistentMountingWithConfigFile`, `executeTestsForPersistentMountingWithConfigFile`, and `RunTestsWithConfigFile`.

Control flow: transforms flags by removing `--o=`, changing hyphens to underscores, stripping doubled underscores, and restoring `_1` to `-1`; appends each as separate `-o` option after bucket, mount point, trace severity, and log file; mounts through `setup.SbinFile`; then runs tests for each flag set.

State/persistence behavior: creates persistent mount process state and writes logs through gcsfuse. It does not create its own durable files beyond the configured log.

Dependencies/integration: consumes `test_suite.TestConfig`, `mounting.MountGcsfuse`, `setup.ExecuteTestForFlagsSet`, and the mount helper built or installed by setup.

Risks/test signals: flag rewriting is string-based and can corrupt values containing hyphens or `_1` sequences unrelated to negative values. Tests using persistent mounting validate whether translated options still behave as intended.
