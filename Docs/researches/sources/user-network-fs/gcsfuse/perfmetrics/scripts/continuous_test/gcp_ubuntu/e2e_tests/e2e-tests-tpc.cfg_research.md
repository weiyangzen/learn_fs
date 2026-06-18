## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/e2e-tests-tpc.cfg

Purpose: Kokoro job configuration for TPC-universe end-to-end tests. It declares artifacts for failed integration logs and Sponge logs, strips them relative to `github/gcsfuse/perfmetrics/scripts`, and dispatches to `gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/tpc_build.sh`.

APIs and integration: This is a Kokoro config, not executable code. The main contract is the `build_file` path plus artifact regexes consumed by Kokoro.

Control flow and state: Kokoro runs the referenced shell script; this file persists no local state. Artifact matching is the only output behavior.

Dependencies and risks: It depends on Kokoro path conventions and the build script staying at the configured path. Risk is low but artifact regex drift can hide failure evidence.

Test signals: Validation is operational: a Kokoro run should invoke `tpc_build.sh` and collect matching logs.
