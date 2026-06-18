# Research: sources/sync-backup/syncthing/test/cli_test.go

## sources/sync-backup/syncthing/test/cli_test.go

Purpose: integration tests for Syncthing CLI startup and home/database generation/reset behavior.

Important APIs/functions: `TestCLIReset`, `TestCLIGenerate`, and `TestCLIFirstStartup`. They run `../bin/syncthing` with `--reset-database`, `--generate`, or `--home` and inspect resulting filesystem state.

Control flow: reset test creates an index directory, runs reset, then ensures it is removed. generate test removes `home.out`, invokes generation, and checks config and key/cert files. first-startup test starts Syncthing with `STNORESTART=1`, concurrently waits for required files and process exit, then kills the process after creation succeeds.

State and persistence: mutates `h1/index-v0.14.0.db`, `home.out`, generated certificates, keys, and reset backup directories.

Dependencies and integration: external built binary, OS process management, local filesystem. Risks include port/environment leakage, process timing races, and stale generated files. Test signal is file existence and process exit behavior.
