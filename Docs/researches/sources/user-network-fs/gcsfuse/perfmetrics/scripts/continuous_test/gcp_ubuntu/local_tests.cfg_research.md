## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/local_tests.cfg

Purpose: Kokoro config for local Ubuntu performance tests, including HNS and flat logs plus FIO output.

APIs and integration: Dispatches to `gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/build.sh` with `BENCHMARK_TYPE=local_tests`; Kokoro collects four gcsfuse log files, `fio-output.json`, and Sponge logs.

Control flow and state: No runtime logic here. The config defines a 300-minute timeout and delegates behavior to the shared Ubuntu build script.

Dependencies and risks: Relies on `BENCHMARK_TYPE` being understood by the build script and artifact names matching produced logs. If filenames change, benchmark results may run but not be archived.

Test signals: Successful Kokoro execution should upload the configured artifacts and complete within the timeout.
