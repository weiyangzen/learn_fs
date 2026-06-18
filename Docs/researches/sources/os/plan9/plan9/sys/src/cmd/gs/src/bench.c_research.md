# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/bench.c

This is a simple Ghostscript-adjacent benchmark program containing both C benchmarks and a large embedded PostScript benchmark script in comments.

Core C behavior:
- Provides dummy Ghostscript external symbols and stubs so it can include Ghostscript timing glue.
- Includes `gp_unix.c` directly to use `gp_get_usertime`.
- Allocates a memory buffer and runs timing loops for integer add/multiply/divide, floating add/multiply/divide, float-int conversion, fast local memory shuffling, and slower strided memory access.
- Prints elapsed time in milliseconds for each benchmark.

Benchmark functions:
- `iadd`, `imul`, `idiv` use loop-unrolled integer operations.
- `fadd`, `fmul`, `fdiv`, `fconv` exercise floating-point arithmetic and conversions.
- `mfast` cycles a small fixed working set.
- `mslow` accesses a wider memory region using a changing offset.

The commented PostScript section contains an equivalent interpreter benchmark for arithmetic, memory/string operations, and font rendering/cache behavior, plus sample outputs from historical machines.

Filesystem relevance:
- `gp_open_scratch_file` is stubbed to return `NULL`; the benchmark does not create or exercise real files.
- Its only practical link to OS behavior is timing and memory performance.
