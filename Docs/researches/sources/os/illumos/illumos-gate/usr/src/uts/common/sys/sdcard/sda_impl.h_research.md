# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdcard/sda_impl.h

## Purpose
Private SD-card framework implementation header defining slot/host soft-state and internal command, initialization, memory-card, nexus, and slot-management functions.

## Main Interfaces
- `sda_slot_t` and `struct sda_slot`: per-slot state including host/private pointers, child devinfo, insertion/failure/init/suspend/detect/fault state, OCR/RCA/clock, current transfer, command/abort lists, ops copy, recursive slot lock, event lock/CV, task queues, cfgadm timestamps, parsed CID/CSD/card geometry, write-protect fields, and block-device handle.
- Slot flags: writable, 4-bit, IF_COND, MMC, SD memory, SDIO, SDHC, memory/SD masks.
- Slot capabilities: no PIO, high speed, 4-bit.
- `struct sda_host`: devinfo, slot count/array, DMA attributes, nexus linkage, attach/open flags.
- Property helper macros `sda_setprop`, `sda_getprop`.
- Internal functions for command allocation/submission/completion, card initialization, memory card block-device operations, nexus open/close/ioctl/bus control, slot lifecycle, power, transfer, fault, and logging.

## Dependencies And Relationships
Includes list, synchronization, block-device, DDI/SunDDI, and public `sys/sdcard/sda.h`. Used by the SD-card framework implementation files.

## Research Notes
The slot has two locking domains: recursive slot ownership via `s_lock` and event notification via `s_evlock`.

## Notable Risks
- Slot state transitions cross task queues, hotplug detection, suspend/resume, and transfer completion.
- Duplicate `sda_slot_reset` declarations appear in the prototype list.
- Parsed CID/CSD geometry feeds block-device read/write behavior, so bit extraction and address shift handling are data-path sensitive.
