<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/improved_e2e_test.sh -->
# sources/user-network-fs/gcsfuse/tools/cd_scripts/improved_e2e_test.sh

Purpose: Newer wrapper for release E2E testing that validates command-line options, optionally selects a release package to install, and delegates actual test execution to `tools/integration_tests/improved_run_e2e_tests.sh`.

Important APIs, types, and functions: Defines `log_info`, `log_error`, `usage`, parses long options with `getopt`, and builds an `ARGS` array. Supported options are `--local-run`, `--release-package-bucket`, `--release-version`, `--zonal`, `--output-dir`, and `--help`.

Control flow: The script enables `set -euo pipefail`, parses options, enforces release bucket/version unless `--local-run` is set, detects Debian/Ubuntu vs RHEL/CentOS from `/etc/os-release`, appends `--install-package-from-path` for package mode, sets package-level parallelism to 4, adds zonal/regional choice, output directory, excludes `cloud_profiler`, sets flake attempts to 3, then invokes the improved runner.

State and persistence behavior: Creates the output directory and may cause the delegated runner to install packages, run tests, and write logs. This wrapper itself mostly constructs arguments and logs to stdout/stderr.

Dependencies and integration points: Depends on GNU `getopt`, OS release metadata, `dpkg` or `uname`, release package bucket naming conventions, and `improved_run_e2e_tests.sh`. It is intended to replace or simplify the legacy `e2e_test.sh` startup flow.

Risks and test signals: Release version regex only accepts plain `MAJOR.MINOR.PATCH`, so beta or build metadata versions are rejected. RHEL detection checks ID/ID_LIKE for `rhel` or `centos` but not `rocky`. Stronger shell settings reduce silent failure. Final signal comes from the delegated runner's exit code and output directory artifacts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/cd_scripts/improved_e2e_test.sh -->
