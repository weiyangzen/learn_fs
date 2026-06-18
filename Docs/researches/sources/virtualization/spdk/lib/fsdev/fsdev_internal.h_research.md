# File Research: sources/virtualization/spdk/lib/fsdev/fsdev_internal.h

## Purpose
Small internal header for fsdev implementation files.

## Contents
- Declares `fsdev_io_submit(struct spdk_fsdev_io *fsdev_io)`.
- Declares `fsdev_channel_get_io(struct spdk_fsdev_channel *channel)`.
- Defines `__io_ch_to_fsdev_ch(io_ch)` as an SPDK IO-channel context cast to `struct spdk_fsdev_channel`.

## Dependencies
Includes `spdk/thread.h`; relies on fsdev structs declared in public/internal fsdev headers.
