# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/txt.c

This is the SPARC backend initialization, register management, instruction emission, typed move lowering, opcode selection, and cleanup file.

`ginit()` sets target identity, initializes registers, listing formats, special nodes (`.safe`, `.rathole`, `.ret`), string/rathole state, and 64-bit support. `gclean()` validates register state, flushes string data, emits globals, appends `AEND`, and calls `outcode()`.

The file provides temporary/register allocation (`regalloc`, `regfree`, `regret`, `regsalloc`, `regaalloc`), argument generation (`gargs`, `garg1`), address conversion (`naddr`, `raddr`), and branch/pseudo-op emission.

`gmove()` is the largest semantic section: it handles loads, stores, integer/floating conversions, special floating constants, memory-register staging, sign/zero extension, unsigned long to float adjustment, and rathole use for conversion through memory. `gopcode()` maps compiler ops to SPARC opcodes and emits comparisons plus branches.

The file also defines target type widths, cast compatibility masks, small immediate checks, external register allocation, branch patching, and pseudo-op creation. It is the backend’s instruction-selection core.
