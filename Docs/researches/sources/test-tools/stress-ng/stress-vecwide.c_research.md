## sources/test-tools/stress-ng/stress-vecwide.c

Purpose: Implements `vecwide`, measuring behavior across increasingly wide integer vector types.

Important APIs/types/functions: `stress_vecwide_info`, generated `stress_vecwide_*` functions, `vec_args_t`, and `stress_vecwide`; uses vector widths from 32 to 2048 bits by default, optional very small/wide builds, target clones, and metrics.

Control flow: allocates a page-aligned argument/result block, fills byte arrays, then loops over vector-width functions. Each function copies byte arrays into vector locals, performs repeated add/sub/xor/mul operations, stores results, and emits bytes to put sinks. Optional verification runs the same function twice and compares result buffers.

State and persistence: anonymous mmap for vector arguments; static metrics per width; no files or child processes.

Dependencies/integration: compiler vector extensions, SIGILL catch, target clone support, stress-ng metrics/debug output.

Risks: extremely wide vector types can stress compiler backends and instruction selection; note a likely typo copies `vec_args->v23` into local `v3`, making the workload use 23 rather than 3 for that vector input.

Test signals: `VERIFY_OPTIONAL`; reports per-width ops/sec and instance-zero duration share/performance comparison.
