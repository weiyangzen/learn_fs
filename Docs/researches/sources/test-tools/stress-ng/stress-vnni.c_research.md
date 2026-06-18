# sources/test-tools/stress-ng/stress-vnni.c

## Purpose
Implements `vnni`, a vector neural network instruction stressor. It exercises VNNI/AVX integer operations via intrinsics when available and generic equivalents otherwise, with deterministic checksum verification.

## Important APIs, types, and functions
`stress_vnni()` is the entry point. `stress_vnni_method_t` maps method names, function pointers, capability probes, endian-specific checksums, and intrinsic flags. Methods cover `vpaddb`, `vpdpbusd`, and `vpdpwssd` in generic and optional 128/256/512-bit intrinsic forms. `stress_vnni_exercise()` performs 1024 calls, times them, checksums `result`, and validates output.

## Control flow
The stressor catches `SIGILL`, seeds deterministic 256-byte input buffers, reads `vnni-method` and `vnni-intrinsic`, probes method capabilities, skips unsupported selections, synchronizes, and then repeatedly exercises either one method or all capable methods. The loop stops on checksum failure or global stop, then emits per-method operation-rate metrics.

## State and persistence
Static buffers hold inputs and latest result. `stress_vnni_data[]` holds capability and metrics. Flags track endian, intrinsic-only mode, and checksum health. No persistent state is written.

## Dependencies and integration points
Registered as `stress_vnni_info` with `CLASS_CPU | CLASS_INTEGER | CLASS_COMPUTE | CLASS_VECTOR`, method/intrinsic options, and `VERIFY_ALWAYS`. Depends on stress-ng CPU feature helpers, target-clone macros, `<immintrin.h>` when available, signal handling, random initialization, and metrics.

## Risks and edge cases
Intrinsic execution depends on accurate CPU/compiler feature detection; `SIGILL` handling mitigates unusual cases. Generic methods let the stressor run without VNNI unless intrinsic-only mode is requested. Endian-specific checksums avoid false failures across byte order.

## Test signals
Checksum mismatch logs actual and expected values and returns failure. Capability skips report unavailable methods. Metrics report `<method> ops per sec`.
