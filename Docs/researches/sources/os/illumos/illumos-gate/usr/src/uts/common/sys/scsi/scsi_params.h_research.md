# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_params.h

## Purpose
Defines common SCSI sizing parameters for sense keys, tags, targets, and LUN counts.

## Main Interfaces
- `NUM_SENSE_KEYS`
- `NTAGS`
- `NTARGETS`, `NTARGETS_WIDE`, `NLUNS_PER_TARGET`
- LUN count helpers: `SCSI_1LUN_PER_TARGET`, `SCSI_8LUN_PER_TARGET`, `SCSI_16LUNS_PER_TARGET`, `SCSI_32LUNS_PER_TARGET`

## Dependencies And Relationships
Included by `scsi_types.h` and therefore broadly visible to SCSI drivers.

## Research Notes
The target/LUN constants are rooted in parallel SCSI defaults but are still used as general defaults for nexus/target drivers.

## Notable Risks
- Modern transports can exceed legacy target/LUN assumptions; drivers should not hard-code these where transport properties provide real limits.
