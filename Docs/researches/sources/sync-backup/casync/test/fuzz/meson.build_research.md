# sources/sync-backup/casync/test/fuzz/meson.build

Purpose: registers fuzz targets with the Meson build.

Important APIs/types/functions: defines executable targets for fuzzers, including linking the common runner or libFuzzer engine depending on build options.

Control flow/state: build-time only; conditional options decide whether fuzzers are regular executables or sanitizer/fuzzer artifacts.

Dependencies/integration: used by `oss-fuzz.sh` and Meson `fuzzers` target.

Risks/test signals: missing source/link dependencies can make fuzzers build but not exercise the intended code. OSS-Fuzz script is the integration check.

Source research group: `subset-b-009122`.
