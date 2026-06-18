<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/cloud_profiler/cloud_profiler_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/cloud_profiler/cloud_profiler_test.go

Purpose: TestMain for Cloud Profiler integration tests, configuring unique service/version labels and mounting gcsfuse with profiler flags.

Important APIs, types, and functions: Constants define test directory, suffix, retry timings, and lexicographic ID alphabet. `getDecreasingString` generates a fixed-length string that sorts newer test identifiers earlier. `TestMain` prepares `testServiceName`, `testVersionName`, config flags, storage client, test environment, and static mount execution.

Control flow: `TestMain` parses setup flags, generates unique profiler service/version names, loads config or creates a default profiler config, substitutes `${PROFILE_LABEL}` and `${PROFILE_SERVICE_NAME}` placeholders when present, initializes Cloud Storage, handles mounted-directory mode, builds flag sets, sets up test dir, runs tests with static mounting, and cleans up the GCS directory.

State and persistence behavior: Creates global service/version identifiers, mounts gcsfuse with profiler enabled, creates a test bucket directory, and deletes it after tests. Cloud Profiler profiles are external GCP state and are queried by companion tests.

Dependencies and integration points: Depends on Cloud Storage, gcsfuse integration setup, static mounting, Cloud Profiler flags, and logger. It sets up globals consumed by `with_gcp_profiler_service_test.go`.

Risks and test signals: Cloud Profiler availability is eventual and external. The decreasing string is designed to reduce API pagination work by making newer deployments sort earlier. Default config enables multiple profiler types and is excluded from release wrapper due to stability TODO.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/cloud_profiler/cloud_profiler_test.go -->
