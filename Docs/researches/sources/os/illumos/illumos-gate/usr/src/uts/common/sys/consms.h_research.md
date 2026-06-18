# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/consms.h

`consms.h` defines private console mouse state. It sets default screen dimensions and pointer acceleration parameters, plus helper `CONSMS_MAX`.

The file defines lower-queue state, ioctl reply callback type, lower queue records, response records, message records, and aggregate console mouse state, covering queued messages, screen/parameter state, and STREAMS coordination.
