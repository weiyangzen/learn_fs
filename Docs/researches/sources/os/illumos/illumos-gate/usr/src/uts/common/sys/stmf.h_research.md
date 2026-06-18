# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stmf.h

## Role

Core SCSI Target Mode Framework API header for LU providers, port providers, SCSI sessions, tasks, data buffers, state changes, task control, and SCSI helper routines.

## Key Contents

Defines STMF structure IDs, provider callback commands/flags, `data_seg_handle_t`, constants, scatter/gather entries, `stmf_data_buf_t`, data-buffer flags, and the central `scsi_task_t` structure. Task fields include provider/private handles, session/lport/LU pointers, LUN, task flags, priority, task management function, buffer counts, command sequence info, expected transfer length, CDB, transfer accounting, status/sense data, and extension pointer.

Defines task flags, task-management codes, additional flags, buffer limits, status controls, I/O flow flags, allocation flags, state-change structures, reason flags, abort commands, control commands for LU/LPORT state changes, info command classifiers, event constants, DDI node type strings, VPD bits, and a seconds-to-ticks helper.

## Interfaces

Declares STMF allocation/free, task allocation/posting, dbuf allocation/setup/xfer/free, status send/completion callbacks, task done/abort/poll, control, ITL handle registration, event registration, SCSI VPD/devid/status helpers, transport ID validation/comparison, remote port allocation/free, LU hold/release, and abort-state query.

## Design Notes

This header is the in-kernel contract between STMF core, logical-unit providers, and port providers. The structures encode both SCSI protocol state and provider-private extension points.
