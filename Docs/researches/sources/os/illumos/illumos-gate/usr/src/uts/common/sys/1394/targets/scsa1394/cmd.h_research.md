# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/scsa1394/cmd.h

## Purpose

`cmd.h` defines the SCSA1394 command object used to carry illumos SCSI packets over SBP-2/IEEE 1394.

## Main Types

`scsa1394_cmd_seg_t` describes one data-buffer or page-table segment with length, device/bus addresses, and a 1394 address handle.

`scsa1394_cmd_t` embeds an `sbp2_task_t` and ends with an embedded `scsi_pkt`. It stores command state/flags, owning LUN, `buf`, SCSI packet, CDB/status/private lengths, inline CDB/status/private storage, timeout tracking, DMA state for the command ORB, data buffer DMA windows and segments, page-table DMA memory, and Symbios workaround bookkeeping for LBA/block breakup.

## Macros and Flags

The header provides conversion macros between packet, command, and SBP-2 task objects. Command states are init/start/status. Flags track extended CDB/private/status allocations, valid DMA resources, map-in state, read/write direction, and Symbios command breakup.

## Research Notes

This is a core storage-adjacent header: it bridges SCSA packet state to SBP-2 task state and owns the DMA metadata needed for FireWire storage transfers.
