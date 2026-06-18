# File Research: sources/os/plan9/9front/sys/src/cmd/disk/smart/ata.c

## Purpose
Implements ATA/SATA SMART probing, enabling, and status checks for `disk/smart`.

## Key Behavior
- Defines ATA passthrough request/reply structures matching Plan 9 sd raw command handling.
- `issueata()` writes an ATA command wrapper, performs the requested data phase, reads the returned status FIS, and tolerates non-ATA kernels during probes.
- `issueatat()` builds common ATA commands from a table: NOP, identify, identify packet, SMART, and signature.
- `ataprobe()` reads the device signature, runs identify, extracts features with FIS helpers, and succeeds only when SMART is advertised.
- `smartfis()` and `smartrsfis()` build SMART enable and return-status FIS commands.
- `ataenable()` enables SMART with subcommand `0xd8`.
- `atastatus()` issues SMART return status and reports `normal` when returned cylinder values are `0x4f/0xc2`, otherwise `threshold exceeded`.

## Interfaces And Dependencies
- Uses `<fis.h>` helpers and embeds `Sfis` in `Sdisk` from `smart.h`.
- Called through the `Dtype` dispatch table in `smart.c`.

## Notes
The implementation is specific to Plan 9 sd ATA passthrough conventions and treats many transfer failures during probing as “not this transport” rather than fatal.
