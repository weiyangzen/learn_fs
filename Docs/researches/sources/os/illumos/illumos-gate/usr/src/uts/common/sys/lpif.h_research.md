# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lpif.h

## Role

SCSI Target Mode Framework (STMF) logical-unit provider interface header.

## Structure

Includes STMF definitions, defines LPIF revisions, `stmf_lu_t` with provider/private fields and LU callback vector, abort commands, LU active/standby states, proxy message types and read/write flags, ITL removal reasons, `stmf_lu_provider_t`, and STMF LU/provider registration and helper function prototypes.

## Dependencies And Consumers

Depends on `sys/stmf_defines.h` and `sys/stmf.h`, including SCSI task/data buffer types. Consumers are logical unit provider drivers and STMF core.

## Important Details

The LU callback table is the core contract: allocation, new task, dbuf transfer completion, status completion, task free, abort, poll, control, info, event handling, dbuf free, and task done. `lp_lpif_rev` is currently expected to be `LPIF_REV_2`.

## Research Notes

Read completely: 146 lines, 4506 bytes.
