# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_fwlog.h

## Purpose
Defines sparse internal register ranges used by PMCS firmware forensics and register-dump collection.

## Main Interfaces
- `pmcs_sparse_regs_t` describes a sparse register segment with shift address, base address, offset start/end, block flags, and optional description.
- Flags identify block starts/ends and a specific SSPA control-register bit.
- `hsst_state[]`, `sspa_state[]`, and `gsm_spregs[]` enumerate hardware/firmware forensic register blocks, including HSST, SSPA, SRC, BDMA, PCIe APP/PHY/CORE, OSSP, LMS_DSS, SSPL_6G, MBIC IOP/AAP1, SPBC, and a large GSM sparse range.

## Dependencies And Relationships
Used by PMCS register-dump/forensics routines declared in `pmcs_proto.h`. The address ranges are based on a PMC firmware forensic application note referenced in the file comment.

## Research Notes
This header contains data definitions, not just declarations, so its include pattern matters. It is a diagnostic map rather than command-path logic.
