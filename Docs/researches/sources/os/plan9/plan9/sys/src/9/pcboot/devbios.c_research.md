# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/devbios.c

## Purpose
Read-only bootstrap device for BIOS INT 13h EDD/LBA disk access, exposed as a Plan 9 device and usable as a `Bootfs` disk backend.

## Main Interfaces
- Exports `biosinit0`, `biossize`, `biossectsz`, `biosread0`, `biosseek`, and `biosgetfspart`.
- Defines `Dev biosdevtab`.
- Provides `sectread` for single-sector BIOS reads.

## Implementation Notes
- Probes BIOS disk count from BDA `0x475`, then scans drive IDs starting at `0x80`.
- Requires extended disk-drive support with fixed disk and EDD capability bits.
- Uses real-mode INT `0x13` via `realmode(Ureg*)`, with requests staged below 64 KiB.
- `sectread` uses `BIOSXCHG` as low-memory exchange buffer and a `Dap` packet for extended reads.
- `extgetsize` uses BIOS function `0x48` to fill sector size and total sector count.
- Device namespace exposes a top-level `bios` directory and `data` file; writes fail because the device is read-only.
- `biosgetfspart` constructs a `Bootfs` and calls `dosinit` on a named partition, typically `9fat`.

## Dependencies And Risks
- Comments warn that BIOS implementations can hang or time out, especially VMware.
- Reset is present but avoided because it hangs some BIOSes.
- Real-mode buffers must remain below 64 KiB and avoid segment-boundary hazards.
