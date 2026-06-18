# sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/static_mounting/static_mounting.go

Purpose: standard static bucket mounting harness for integration tests.

Important APIs/types/functions: `MountGcsfuseWithStaticMountingWithConfigFile`, deprecated `MountGcsfuseWithStaticMounting`, `executeTestsForStaticMounting`, and `RunTestsWithConfigFile`.

Control flow: optional TPC endpoint key-file flag is added, default trace log flags plus bucket and mount directory are appended, gcsfuse is mounted with `setup.BinFile`, and each flag set runs through `setup.ExecuteTestForFlagsSet`.

State/persistence behavior: establishes one gcsfuse mount per flag set and writes to the configured gcsfuse log file. It relies on setup globals for binary and endpoint mode.

Dependencies/integration: common entry point for packages such as write-large-files and implicit/explicit directory tests.

Risks/test signals: mutates the supplied `flags` slice by append, so callers reusing backing arrays could see unexpected changes. Failures are detected by mount errors or nonzero test exit codes.
