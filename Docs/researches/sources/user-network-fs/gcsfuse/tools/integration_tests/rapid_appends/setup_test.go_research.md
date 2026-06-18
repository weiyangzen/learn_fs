# sources/user-network-fs/gcsfuse/tools/integration_tests/rapid_appends/setup_test.go

Purpose: Provides rapid-appends package setup, fallback config, zonal-bucket gating, primary/secondary mount paths, storage client, and global constants.

Important APIs/types/functions: constants define test directory, file prefixes, sizes, block size, open modes, metadata TTL, and append counts. `env` stores storage client, context, config, and bucket type. `TestMain` builds fallback config for single/dual appends and reads under multiple cache/kernel-reader combinations.

Control flow: `TestMain` parses setup flags, reads config, synthesizes config if absent, initializes environment, aborts if not a zonal bucket, creates a storage client, handles GKE mounted-directory mode, sets up the GCE test dir, rewrites temp paths, creates a secondary mount directory, runs tests, and finally cleans the rapid-appends prefix.

State/persistence: Global `testEnv` is shared by suites. The secondary mount directory is created under the test temp root. Cleanup removes GCS test objects after `m.Run`.

Dependencies/integration: Uses Cloud Storage, setup/test-suite helpers, client helpers, and operation constants.

Risks/test signals: The package hard-fails outside zonal bucket runs. Fallback config is extensive and must keep primary/secondary flags aligned by index. Passing package setup indicates zonal rapid-append feature coverage is being run with valid mount/cache combinations.
