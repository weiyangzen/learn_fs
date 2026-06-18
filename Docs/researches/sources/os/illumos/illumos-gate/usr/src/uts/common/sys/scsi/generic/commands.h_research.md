# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/commands.h

This generic SCSI header defines standard command opcodes, CDB group sizing, service action constants, MMC event constants, and command-name mappings.

Key definitions:
- Defines CDB group ID extraction and expected CDB lengths for command groups 0, 1, 2, 4, and 5.
- Defines SCSI command opcodes for common, direct-access, sequential-access, printer, processor, WORM, read-only, MMC, variable-length, persistent reservation, security protocol, maintenance, and service-action commands.
- Includes read/write variants for 6-byte, 10-byte, 12-byte, and 16-byte command formats.
- Defines service actions for read capacity/read long/write long, target port groups, supported operations/management, timestamps, device identifiers, priorities, and media serial.
- Defines `SCSI_CMDS_KEY_STRINGS`, a large opcode-to-string initializer used by decoding/logging helpers.
- Includes generic inquiry and sense definitions, then implementation-specific command definitions.

Dependencies:
- Includes `generic/inquiry.h`, `generic/sense.h`, and `impl/commands.h`.

Impact:
- This is the generic opcode namespace used throughout SCSA and SCSI target/HBA drivers.
- The command string macro feeds diagnostics and error reporting.

Cautions:
- Some opcodes overlap by device type, and the string mapping intentionally combines aliases.
- `ATAPI_CAPABILITIES` is explicitly noted as not being a command code and not belonging in this file.
