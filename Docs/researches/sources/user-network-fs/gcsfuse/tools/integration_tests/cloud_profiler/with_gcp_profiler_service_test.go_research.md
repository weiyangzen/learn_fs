<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/cloud_profiler/with_gcp_profiler_service_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/cloud_profiler/with_gcp_profiler_service_test.go

Purpose: Integration test that verifies a real Cloud Profiler profile appears for the gcsfuse service/version configured by the package TestMain.

Important APIs, types, and functions: `CloudProfilerSuite` defines `writeSingleRandomFile` to generate write load, `getGCPProjectID` to resolve project from metadata or environment, `checkIfProfileExistForServiceAndVersion` to page through Cloud Profiler API profiles, and `TestValidateProfilerWithActualService` to retry until a matching profile exists. `TestCloudProfilerSuite` runs the suite.

Control flow: The test obtains a project ID, creates a Cloud Profiler API client, then calls `operations.RetryUntil` for up to 10 minutes. Each retry writes a 100 MiB random file through the mount to stimulate profiling and scans profile pages for deployment target equal to `testServiceName` and version label equal to `testVersionName`.

State and persistence behavior: Writes large random files into the mounted bucket and relies on Cloud Profiler backend state. It does not delete individual load files directly; package cleanup removes the test directory.

Dependencies and integration points: Depends on GCE metadata or `GOOGLE_CLOUD_PROJECT`, Cloud Profiler v2 API, gcsfuse mount from TestMain, and service/version globals. Requires profiler API permissions and eventual profile ingestion.

Risks and test signals: `getGCPProjectID` shadows `projectID` inside the error branch and may return an empty outer variable if metadata fails but env is set, which is a correctness risk. Pagination uses errors for early exit, including a sentinel success break. The strong signal is a matching profile from the real API; failures may be infrastructure, permission, or eventual-consistency related.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/cloud_profiler/with_gcp_profiler_service_test.go -->
