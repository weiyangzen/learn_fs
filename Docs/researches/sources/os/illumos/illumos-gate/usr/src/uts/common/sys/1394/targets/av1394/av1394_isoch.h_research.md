# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/av1394/av1394_isoch.h

## Purpose

`av1394_isoch.h` defines private isochronous transfer state for the IEEE 1394 AV target driver. It covers DMA buffer pools, receive and transmit IXL command chains, per-channel transfer state, mmap offset allocation, IEC 61883 autotransmit support, and CMP plug-control register state.

## Main Interfaces

The central type is `av1394_ic_t`, representing one isochronous channel with direction, state, packet/frame sizing, 1394 isoch handles, condition variable, deferred request flags, and embedded receive/transmit substate.

Receive state `av1394_ir_t` tracks data pools, IXL receive buffers, full/empty frame queues, overflow index, and read offsets. Transmit state `av1394_it_t` tracks IXL begin/data blocks, frame timestamp metadata, empty/full queues, underrun state, and write offsets.

The header declares lifecycle and I/O entry points for channel open/close/init/fini/start/stop, receive read/recv/overflow, transmit write/xmit/underrun, mmap address-space allocation, CMP init/fini/bus-reset/ioctl handlers, and top-level isoch attach/detach/open/close/read/write/ioctl/devmap operations.

## Data and Synchronization

DMA memory is modeled as `av1394_isoch_seg_t` arrays inside `av1394_isoch_pool_t`, with DDI umem and DMA cookies. Comments and `_NOTE` annotations mark much of the setup data as single-threaded after initialization. `av1394_isoch_t` is the per-instance state with an instance mutex, channel array, CMP registers, soft interrupt state, and autotransmit configuration. Lock ordering is explicitly `i_mutex` before `ic_mutex`.

## Research Notes

This file is a private contract between AV1394 isochronous implementation files. Storage relevance is indirect, through common illumos DMA, devmap, soft interrupt, and 1394 target-driver patterns rather than filesystem behavior.
