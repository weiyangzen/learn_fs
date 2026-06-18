# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_iomb.h

## Purpose
Defines PMC IO Message Buffer protocol constants, inbound/outbound opcodes, status values, NVRAM/VPD/register-dump payloads, IOMB header layout, and queue producer/consumer helper macros.

## Main Interfaces
- IOMB header bit macros define valid/high-priority, buffer count, outbound queue ID, category, and opcode fields.
- Inbound opcodes cover echo/info/VPD, PHY start/stop, SSP/SMP/SATA I/O, aborts, device handle registration/deregistration, local PHY control, firmware flash, GPIO, diagnostics, timestamp, port control, NVMD data, and device state.
- Outbound opcodes cover completions, async events, registration results, abort results, diagnostics, queue skipping, device handle removal, and device-state responses.
- Status constants cover generic completion, link/open connection failures, SATA/NCQ errors, SMP errors, device-state/recovery errors, NVMD/flash errors, device-registration outcomes, and SAS hardware events.
- `pmcs_get_nvmd_cmd_t`, `pmcs_set_nvmd_cmd_t`, `pmcs_vpd_header_t`, `pmcs_vpd_kv_t`, `pmcs_iomb_header_t`, and `pmcout_ssp_comp_t` model wire-format payloads.
- Queue macros implement circular IQ/OQ indexing, IQ entry acquisition, producer-index updates, DMA sync, and OQ consumer updates.

## Dependencies And Relationships
Relies on `pmcs_param.h` queue sizes, `pmcs_hw_t` queue fields from `pmcs.h`, and register accessors from `pmcs_reg.h`. It is the core hardware/firmware message protocol layer for PMCS.

## Research Notes
The comments explain directionality clearly: inbound queues are host-to-card with card-side producer doorbells, outbound queues are card-to-host with host-side consumer updates.
