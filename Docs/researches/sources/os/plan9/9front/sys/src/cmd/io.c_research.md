# File Research: sources/os/plan9/9front/sys/src/cmd/io.c

Implements low-level port/device register read/write utility.

Key points:
- Usage supports size selectors:
  - default byte
  - `-W` 2 bytes
  - `-L` 4 bytes
  - `-M` 8 bytes
- Selects default device files by size: `#P/iob`, `#P/iow`, `#P/iol`, or `#P/msr`.
- `-E` redirects all size device files to `#P/ec`.
- `-f file` overrides device file.
- `-r` reads; `-w` writes.
- Takes address, optional write value, and optional mask.
- Uses `pread`/`pwrite` at the numeric address offset, little-endian encodes/decodes up to 64-bit values, applies masks, and prints final value.

Dependencies and interactions:
- Uses Plan 9 processor-port device files.

Research relevance:
- A privileged diagnostic/control tool for direct I/O, EC, or MSR access.
