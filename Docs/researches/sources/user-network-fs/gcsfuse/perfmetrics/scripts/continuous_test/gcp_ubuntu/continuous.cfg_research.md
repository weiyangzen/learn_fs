# sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/continuous.cfg

## Purpose

Kokoro job configuration for the gcsfuse Ubuntu continuous perfmetrics workflow.

## Important APIs, Types, and Functions

Defines artifacts for flat/HNS fio and ls logs, `fio-output.json`, and Sponge logs. Sets `strip_prefix`, `timeout_mins: 360`, and `build_file` pointing to `continuous_test/gcp_ubuntu/build.sh`.

## Control Flow

Kokoro runs the configured build file and collects matching artifacts. Benchmark selection is delegated to environment variables consumed by the build script.

## State and Persistence Behavior

Controls artifact persistence and path stripping. Does not manage runtime state directly.

## Dependencies and Integration Points

Integrates with Kokoro artifact handling, Sponge logs, and the perfmetrics build script. Regexes must match downstream output filenames.

## Risks and Edge Cases

Renamed logs will not be collected. Six-hour timeout can delay feedback for hung jobs. Strip prefix and regex path assumptions must stay aligned with Kokoro checkout layout.

## Test Signals

Kokoro invokes the expected build script and artifact tabs contain fio/ls logs, fio JSON, and Sponge logs.
