# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/status.h

## Purpose
Provides an implementation-specific SCSI status size constant.

## Main Interfaces
- `STATUS_SIZE`: fixed status block allocation size of 4 bytes.

## Dependencies And Relationships
No external includes. This complements generic SCSI status definitions and allocation code that needs a default status buffer size.

## Research Notes
The file is intentionally tiny and only wraps the constant in standard include guards and C++ linkage guards.

## Notable Risks
- Code assuming richer status layout must use the generic status structures, not this allocation-size constant alone.
