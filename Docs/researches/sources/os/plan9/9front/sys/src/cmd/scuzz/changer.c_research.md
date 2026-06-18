# File Research: sources/os/plan9/9front/sys/src/cmd/scuzz/changer.c

Purpose: Implements SCSI medium changer commands.

Key routines:
- `SReinitialise`: initialize element status.
- `SRmmove`: move medium from source to destination with optional invert bit.
- `SRestatus`: read element status for a type and requested allocation length.

Integration: Invoked by `scuzz.c` handlers `einit`, `mmove`, and `estatus`.

Risks:
- Minimal validation; caller parses and bounds arguments.
- Command buffers assume synchronous request lifetime.
