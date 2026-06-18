# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/dtracy.c

This is the main dtracy command driver. It initializes parsing, installs formatters, connects to the kernel dtracy device, uploads generated programs, reads epid mappings, and streams trace and aggregation output.

Key responsibilities:
- Provides allocation wrappers `emalloc`, `erealloc`, `dtmalloc`, and `dtfree`.
- Defines built-in variables (`arg0`-`arg9`, `pid`, `machno`, `time`, `probe`) in `globvars`.
- Opens `#Δ/clone`, discovers the dtracy instance number, and opens the trace buffer in `setup`.
- Packs and writes compiled clauses to the kernel `prog` file in `progcopy`.
- Reads epid-to-clause mappings from the kernel `epid` file in `epidread`.
- Streams buffers through `parsebuf` in `bufread`.
- Forks an aggregation reader in `aggproc` when aggregations are present.

Important implementation notes:
- `-d` runs a compile/debug dump instead of attaching to the kernel device.
- Aggregation reading uses shared memory `rfork(RFPROC|RFMEM)` so interruption state can be shared.
- Runtime output uses a `Biobuf` around stdout for normal trace records.
