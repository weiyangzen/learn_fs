# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9ping.c

Microbenchmark utility for repeated small reads or writes against a file descriptor or file.

Key behavior:
- Parses `-n count`, `-s size` with optional `k`, `m`, or `g` suffix, `-r`, and `-w`.
- Opens an optional target file or uses fd 0.
- Repeats `pread()` or `pwrite()` at offset zero `n` times and records elapsed microseconds between operations.
- Prints average, min, max, and standard deviation.

Important implementation details:
- Size is restricted to 1 through 1 MiB.
- Timing uses `nsec()` and converts to microseconds.

Risks and invariants:
- Does not initialize write buffer contents.
- The benchmark repeatedly uses offset zero, so it measures latency/cache behavior rather than sequential throughput.
