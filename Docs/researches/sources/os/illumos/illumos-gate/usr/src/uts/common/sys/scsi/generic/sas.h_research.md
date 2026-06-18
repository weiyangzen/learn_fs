# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/sas.h

This header defines simplified common SAS address frame, open address frame, SSP command/response IU, link-rate, protocol, and task-management constants.

Key definitions:
- Defines `sas_identify_af_t` and `sas_open_af_t` for SAS address frames, excluding trailing CRC.
- Defines SAS address frame type, device type, protocol, support, connection rate, SATA support, and attached-name offset constants.
- Defines `sas_ssp_cmd_iu_t` for SSP command information units and `sas_ssp_rsp_iu_t` for SSP response information units.
- Defines task attributes, response data presence values, response/TMF result codes, task management function codes, PHY number limits, and maximum SMP payload size.

Dependencies:
- Includes `sys/sysmacros.h` for `DECL_BITFIELD*` helpers.

Impact:
- Provides shared SAS protocol structures for HBA/SAS code without pulling in the full SMP frame catalog.

Cautions:
- Comments note the definitions are simplified/reduced from SAS-2 material.
- Structures include variable trailing payloads and exclude CRC where noted.
