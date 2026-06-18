# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/bench.c

This file is a simple Ghostscript-era hardware benchmark suite with both C and embedded PostScript benchmark text. It is not part of filesystem behavior.

Key responsibilities:
- Patches minimal Ghostscript external symbols so it can include/use Ghostscript platform timing code.
- Captures `stdout`, `stderr`, and debug output handles for Ghostscript-style I/O globals.
- Includes `gp_unix.c` directly to access `gp_get_usertime`.
- Defines CPU and memory microbenchmarks:
  - integer add, multiply, divide
  - floating add, multiply, divide
  - float/int conversion
  - fast local memory movement
  - slower strided memory access
- Runs each benchmark in `main`, times it, prints elapsed milliseconds, and exits.
- Includes historical benchmark output from SPARCstation, 486DX, and Ghostscript/PostScript runs.

Important implementation details:
- `gp_open_scratch_file` is stubbed to return `NULL`.
- `gp_set_printer_binary` and `gs_to_exit` are empty stubs.
- Allocates roughly 1.1 MB for memory benchmarks and frees it on exit.
- The top of the file is also valid enough for Ghostscript/PostScript extraction via the initial comment style.

Notable risks:
- It includes a `.c` file directly, which is deliberate for this standalone benchmark but unusual in normal builds.
- It is old benchmarking code and not a robust modern performance harness.
- No filesystem or storage logic is present.

Research classification: standalone Ghostscript benchmark and historical performance note file.
