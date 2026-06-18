# sources/sync-backup/casync/test/fuzz/fuzz-compress.c

Purpose: libFuzzer target for compression/decompression handling.

Important APIs/types/functions: `LLVMFuzzerTestOneInput` accepts arbitrary bytes, feeds them through casync compression APIs, and validates that the code rejects or round-trips inputs without crashing or leaking under sanitizer builds.

Control flow/state: stateless per fuzz case except heap buffers allocated by compression helpers. The target returns 0 for all inputs so coverage-guided fuzzing can continue.

Dependencies/integration: linked by `test/fuzz/meson.build` and built for OSS-Fuzz via `tools/oss-fuzz.sh`.

Risks/test signals: fuzz value is strongest for malformed compressed streams and allocation edge cases. It is not a semantic corpus test for all compression algorithms unless build options enable them.

Source research group: `subset-b-009122`.
