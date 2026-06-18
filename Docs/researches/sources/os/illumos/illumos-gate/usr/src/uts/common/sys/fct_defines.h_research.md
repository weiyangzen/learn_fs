# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fct_defines.h

## Role

`fct_defines.h` supplies constants shared by the Fibre Channel Target framework. It maps FCT statuses to STMF statuses, defines FCT events, ELS/BLS/name-service opcodes, PRLI bits, FCP control/status bits, well-known addresses, WWN lengths, and forward declarations.

## Status And Events

- `fct_status_t` aliases `stmf_status_t`.
- Defines success/failure/busy/abort/not-found/timeout statuses and FCA-specific failure space.
- Defines FCT-specific failure codes for stuck worker, allocation failure, local port offline, no exchange resources, not logged in, ABTS received, and remote-port reject.
- `FCT_REJECT_STATUS()` embeds reject reason and explanation into a status value.
- Event codes cover link up, link down, link reset, and adapter fatal.

## FC Protocol Constants

- Defines ELS opcodes for LSRJT, ACC, PLOGI/FLOGI/LOGO, ABTX, RLS, ECHO, REC, SRR, PRLI/PRLO, SCN, TPRLO, PDISC, ADISC, RSCN, SCR, and RNID.
- Defines BLS reply opcodes BA_ACC and BA_RJT.
- Defines name server command codes for get/register/deregister operations and CT accept/reject.
- Defines PRLI bits for read/write xfer-rdy disable, initiator/target function, data overlay, FCP confirmation, retry, task retry id, and REC support.
- Defines FC name server class bits and SCR registration function codes.
- Defines FCP control bit helpers for task attributes, task management, reset, task set control, and read/write data direction.
- Defines FCP SCSI status bits for bidirectional response/residual, confirmation requested, residual under/over, sense length valid, and response length valid.

## Address And WWN Helpers

Defines domain controller and well-known address ranges, `FC_WELL_KNOWN_ADDR()`, WWN byte/string buffer lengths, and forward declarations for core FCT structures.
