# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/dcam1394/dcam.h

## Purpose

`dcam.h` is the primary private header for the IEEE 1394 digital camera target driver. It defines device flags, per-buffer DMA metadata, ring-buffer state, and the driver soft-state structure used by attach, open, capture, ioctl, read, poll, interrupt, and bus-reset paths.

## Main Types

`buff_info_t` describes one frame buffer: video mode, sequence number, timestamp, kernel address, DMA/access handles, DMA cookie, memory length, and cookie count.

`ring_buff_t` describes a circular frame buffer with buffer count/size, buffer metadata array, read pointer state, status per reader, and write pointer position. The driver supports one read pointer through `MAX_NUM_READ_PTRS`.

`dcam_state_t` stores the device instance, 1394 attach/target/isochronous handles, mutexes, parameter capabilities, IXL chain pointer, ring buffer, sequence counter, flags, current video mode/frame rate/capacity, status, online/power/suspend state, and bus-reset callback id.

## Interfaces

The header declares standard module and driver entry points, character device operations, interrupt and bus-reset callbacks, ring-buffer management helpers, and frame receive start/stop helpers.

## Research Notes

This is the shared state definition for DCAM driver implementation files. The most important risks are DMA buffer lifetime, ring-buffer reader/write pointer synchronization, and flag transitions around capture, suspend, and bus reset.
