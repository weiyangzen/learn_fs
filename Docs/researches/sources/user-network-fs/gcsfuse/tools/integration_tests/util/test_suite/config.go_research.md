# sources/user-network-fs/gcsfuse/tools/integration_tests/util/test_suite/config.go

Purpose: defines YAML-backed integration-test configuration schemas and loader.

Important APIs/types/functions: `BucketType`, `TestConfig`, `ConfigItem`, top-level `Config`, and `ReadConfigFile`.

Control flow: `ReadConfigFile` reads a file path if non-empty, expands environment variables in the YAML content, unmarshals into `Config`, and returns an empty config when no path is supplied.

State/persistence behavior: reads config from disk but does not write. The resulting structs drive mount paths, buckets, log paths, compatibility, and flag sets across many test packages.

Dependencies/integration: consumed by `setup.BuildFlagSets`, mounting harnesses, and test `TestMain` functions. Uses `gopkg.in/yaml.v3`.

Risks/test signals: load and parse errors call `log.Fatalf`, terminating the process. `GCSFuseMountedDirectory` and log fields are not YAML-tagged, so they are runtime-populated rather than config-file fields.
