## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/micro_benchmarks/continuous.cfg

Purpose: Minimal Kokoro continuous config for micro-benchmarks.

APIs and integration: The sole behavior is `build_file: "gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/micro_benchmarks/build.sh"`, binding the Kokoro job to the remote VM runner.

Control flow and state: No env vars, artifacts, or timeout are declared in this file; defaults come from Kokoro/job configuration and the shell script.

Dependencies and risks: Any output collection must be provided elsewhere. Risk is mostly hidden failure evidence if the build script logs are not configured as artifacts by the job wrapper.

Test signals: A job should invoke `build.sh` successfully.
