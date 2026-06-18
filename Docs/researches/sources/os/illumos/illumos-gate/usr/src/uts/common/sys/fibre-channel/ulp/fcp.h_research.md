# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcp.h

Defines FCP wire-format structures for SCSI over Fibre Channel. It includes FCP frame information categories for SCSI data, command, response, and transfer-ready frames.

Core structures are `fcp_cntl_t`, `fcp_ent_addr_t`, `fcp_cmd_t`, `fcp_status_t`, and `fcp_rsp_t`. These model command task attributes, task management bits, read/write direction, hierarchical LUN addressing, command CDB payload, response status, residual flags, sense length, and response-info length. Bitfield order depends on `_BIT_FIELDS_HTOL` or `_BIT_FIELDS_LTOH`.

The file also defines response-info codes, PRLI and PRLI-ACC payload layouts, unsolicited FCP buffer flags for target/out-of-band commands, maximum response IU size, and FC-4 type bitmap helpers. It is protocol layout, not driver state.
