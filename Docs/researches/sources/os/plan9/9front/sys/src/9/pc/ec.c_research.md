# File Research: sources/os/plan9/9front/sys/src/9/pc/ec.c

## Purpose
Embedded Controller access helper for ACPI-style laptop ECs, typically using command/status port `0x66` and data port `0x62`.

## Exposed Interface
- Kernel helper API:
  - `ecread(uchar addr)`
  - `ecwrite(uchar addr, uchar val)`
  - `ecinit(int cmdport, int dataport)`
- Adds an architecture file:
  - `ec`: 256-byte read/write view of EC address space.

## Implementation Notes
- Maintains global EC state with initialization flag and two ports (`EC_SC`, `EC_DATA`).
- `ecwait()` polls status bits with a timeout and logs status/caller PC on timeout.
- `ecread()` waits for input buffer clear, sends `RD_EC`, writes address, waits for output buffer full, reads data, and waits for output buffer clear.
- `ecwrite()` waits for input buffer clear, sends `WR_EC`, writes address and value, and waits for completion after each stage.
- `ecarchread()` and `ecarchwrite()` expose byte-range reads/writes through `addarchfile`.
- `ecinit()` reserves both I/O ports and registers the arch file.

## Filesystem Relevance
This is a small Plan 9 arch-file bridge from hardware EC address space to a file-like kernel interface. It demonstrates device namespace exposure through `addarchfile` rather than a full `Dev` table.

## Risks / Quirks
- Timeout loop is fixed at 1000 iterations with 1 ms delay.
- No EC burst mode or query command support is exposed despite constants being defined.
- The arch file permits raw EC writes and is therefore privileged by mode `0660`.
