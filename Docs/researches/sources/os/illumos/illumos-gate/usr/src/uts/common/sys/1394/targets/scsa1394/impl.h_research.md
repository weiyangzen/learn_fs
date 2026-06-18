# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/scsa1394/impl.h

## Purpose

`impl.h` is the main private implementation header for the SCSA1394 HBA driver, which exposes SBP-2 FireWire storage devices to the illumos SCSI framework.

## Main Structures

`scsa1394_thread_t` models a per-LUN worker thread with request bits for exit, task status, SBP-2 nudging, bus reset, disconnect, and reconnect.

`scsa1394_lun_t` stores per-LUN locks, SBP-2 LUN/session pointers, child devinfo, worker and soft interrupt state, device workaround flags, fake inquiry data, and per-LUN statistics.

`scsa1394_state_t` stores per-instance device state, 1394 handles, event callbacks, DMA attributes, SCSI HBA transport, SBP-2 target/config ROM, LUN array, command cache, taskq, workaround flags, geometry hints, and instance statistics.

## Helpers and Interfaces

The header defines address/transport/state conversion macros, local node/bus generation macros, SBP-2 address/ORB helpers, CDB LBA and transfer-length extraction macros for 6/10/12-byte and READ CD commands, CD-RW block-size validation, constants, and function prototypes for SBP-2 attach/login/logout/request/reset/flush plus HBA worker and device-state helpers.

## Research Notes

This header is a compact map of FireWire storage driver architecture: per-instance target state, per-LUN work serialization, SBP-2 command conversion, bus reset handling, and legacy device workarounds.
