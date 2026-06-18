# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/flag_optimizations/setup_test.go

Purpose: package-level orchestration for flag optimization tests. It defines fallback config for machine-type/profile/zonal/kernel-reader scenarios and runs the package across static, dynamic, and only-dir mounting modes.
Important APIs/types/functions: constants `testDirName`, `onlyDirMounted`, `GKETempDir`; `env` with mount function/dirs/client/context/config; `mountGCSFuseAndSetupTestDir`, `mustMountGCSFuseAndSetupTestDir`, and `TestMain`.
Control flow: setup parses flags, builds fallback `FlagOptimizations` config with 12 run-specific items, initializes storage client/environment, validates bucket/mounted-directory flags, prepares test bucket and path overrides, runs static tests, then dynamic tests, then only-dir tests if prior modes pass.
State and persistence: creates test directories under `FlagOptimizationsTests` and optional only-dir prefix. Config and mount dirs change between mount modes. Cleanup removes bucket prefixes and saves logs on failure.
Dependencies and integration points: integrates static/dynamic/only-dir mounting helpers, `setup.BuildFlagSets`, `client` helpers, and config consumed by mount, optimization, and zonal kernel-reader tests.
Risks and edge cases: sequential reruns of `m.Run()` depend on package globals being reset by tests. Fallback run names must stay synchronized with test functions. Only-dir cleanup targets a nested prefix.
Test signals: successful pass across mount modes demonstrates optimized flags behave consistently under different mount topologies.
