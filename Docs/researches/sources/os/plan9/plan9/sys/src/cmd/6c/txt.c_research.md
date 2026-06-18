# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/txt.c

This is the amd64 compiler backend’s instruction emission and ABI helper file. `ginit` initializes target state, reserved registers, special nodes, string/rathole symbols, return nodes, and type capability arrays. `gclean` validates register release, flushes string data, emits globals, appends `AEND`, and writes object output.

It implements argument placement (`gargs`, `garg1`, `regaalloc`, `regaalloc1`), temporary stack allocation (`regsalloc`), register allocation/free helpers, return-register selection, address conversion (`naddr`), instruction creation (`gins`), pseudo-op creation, branch generation, and branch patching.

`gmove` is a major conversion/move engine. It handles loads, stores, integer extension/truncation, pointer/vlong moves, float/integer conversions, unsigned-to-float corner cases, float-to-float moves, zero floating constants, and same-register no-ops.

`gopcode` maps compiler tree operations to amd64 opcodes, including integer, pointer, floating, shift, comparison, call, multiply, divide, and modulo forms.

The file also defines target type widths, legal cast masks, external register allocation, small constant checks, and structure/argument alignment policy.
