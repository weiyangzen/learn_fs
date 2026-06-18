<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/e2e_test.sh -->
# sources/user-network-fs/gcsfuse/tools/cd_scripts/e2e_test.sh

Purpose: Legacy release VM startup script that installs prerequisites, installs or builds gcsfuse, runs integration test suites against flat/HNS/zonal/emulator buckets, gathers logs, and uploads results to a GCS release bucket.

Important APIs, types, and functions: Shell helpers include `create_user`, `grant_sudo`, `run_non_parallel_tests`, `run_parallel_tests`, `run_e2e_tests`, `gather_test_logs`, `log_based_on_exit_status`, and `run_e2e_tests_for_emulator_and_log`. It reads GCE metadata for zone and per-instance flags (`custom_bucket`, `run-on-zb-only`, `run-read-cache-only`, `run-light-test`), consumes `version-detail/details.txt`, and runs `go test` under `tools/integration_tests/*` with `--integrationTest`, `--testbucket`, `--testInstalledPackage`, timeout, and conditional `--zonal`.

Control flow: The outer root phase installs/updates gcloud, discovers metadata, creates a privileged local user, and enters a `sudo -u starterscriptuser` subshell. The user phase installs OS dependencies and Go, clones gcsfuse, checks out the release commit, optionally builds from source for custom bucket runs, assembles test package arrays, runs selected suites in parallel/non-parallel buckets, and uploads success/log artifacts in a trap on exit.

State and persistence behavior: Mutates the VM significantly: package installation, gcloud upgrade under `/usr/local`, sudoers file creation, user creation, repository clone, Go install, `/usr/bin`/`/usr/sbin` binary copy for source builds, local logs under home and `/tmp`, GCS uploads under `gs://<bucket>/v<version>/<vm>/`, and test buckets/objects via integration tests.

Dependencies and integration points: Requires GCE metadata server, gcloud, release bucket layout, apt/yum/dnf, Go downloads, GitHub, GCS permissions, integration test utilities, and OS-specific package managers. Integrates with release automation metadata and older gcsfuse versions by conditionally passing `-short` and `--zonal`.

Risks and test signals: Broad operational risk: root package changes, unpinned gcloud download, NOPASSWD sudo user, shell quoting complexity in nested script, and a bug-like variable mismatch in `run_e2e_tests_for_emulator_and_log` (`emulator_test_status` set but `e2e_tests_emulator_status` checked). Test signals are release-level: uploaded success markers per bucket type and consolidated logs for failed package suites.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/e2e_test.sh -->
