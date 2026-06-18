# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/message.h

This header defines parallel SCSI message byte constants and helper macros for classifying message lengths/types.

Key definitions:
- Defines fixed one-byte messages such as command complete, save/restore data pointer, disconnect, initiator error, abort, reject, nop, parity error, linked complete, device reset, abort tag, clear queue, ACA, and LUN reset.
- Defines extended message constants for synchronous negotiation, wide transfer, identify extended, and parallel protocol.
- Defines parallel protocol optional flags for IU, DT, and QAS.
- Defines fixed two-byte queue tag messages.
- Defines identify-message masks and legacy pre-SCSI-3 LUN/target-routine fields.
- Provides `IS_IDENTIFY_MSG`, `IS_IDENTIFY_MSG_SCSI3`, `IS_EXTENDED_MSG`, `IS_2BYTE_MSG`, and `IS_1BYTE_MSG`.

Dependencies:
- No external includes in the file.

Impact:
- Used by legacy/parallel SCSI transport code to parse and emit message phases.

Cautions:
- Several definitions are explicitly pre-SCSI-3 only; SCSI-3 users should use the SCSI-3 identify helper.
